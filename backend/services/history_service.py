"""
Сервис истории цен для построения графиков.
"""
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from backend.database.connection import db
from backend.models.price_history import PriceHistory

logger = logging.getLogger(__name__)


class HistoryService:
    """Сервис работы с историческими данными курсов."""

    @staticmethod
    def get_history(
        symbol: str,
        asset_type: str = 'crypto',
        days: int = 7,
    ) -> Dict:
        """
        Получить историю изменения курса.

        Args:
            symbol: Код валюты или символ криптовалюты.
            asset_type: Тип актива ('currency' или 'crypto').
            days: Количество дней истории.

        Returns:
            Словарь с историей и процентом изменения.
        """
        symbol = symbol.upper().strip()
        asset_type = asset_type.lower().strip()

        if asset_type not in ('currency', 'crypto'):
            return {
                'error': 'Недопустимый тип актива. Используйте currency или crypto.',
                'symbol': symbol,
                'asset_type': asset_type,
            }

        days = max(1, min(days, 90))
        since = datetime.now(timezone.utc) - timedelta(days=days)

        records = (
            PriceHistory.query
            .filter(
                PriceHistory.symbol == symbol,
                PriceHistory.asset_type == asset_type,
                PriceHistory.recorded_at >= since,
            )
            .order_by(PriceHistory.recorded_at.asc())
            .all()
        )

        if not records:
            return {
                'symbol': symbol,
                'asset_type': asset_type,
                'days': days,
                'history': [],
                'change_percent': 0.0,
                'current_price': None,
                'message': 'Исторические данные пока отсутствуют',
            }

        history = [record.to_dict() for record in records]
        change_percent = HistoryService._calculate_change_percent(records)

        return {
            'symbol': symbol,
            'asset_type': asset_type,
            'days': days,
            'history': history,
            'change_percent': change_percent,
            'current_price': float(records[-1].price),
            'first_price': float(records[0].price),
        }

    @staticmethod
    def _calculate_change_percent(records: List[PriceHistory]) -> float:
        """
        Рассчитать процент изменения между первой и последней записью.

        Args:
            records: Список записей истории.

        Returns:
            Процент изменения.
        """
        if len(records) < 2:
            return 0.0

        first_price = Decimal(str(records[0].price))
        last_price = Decimal(str(records[-1].price))

        if first_price == 0:
            return 0.0

        change = ((last_price - first_price) / first_price) * 100
        return round(float(change), 2)

    @staticmethod
    def get_weekly_changes_batch(
        symbols: List[str],
        asset_type: str,
        days: int = 7,
    ) -> Dict[str, float]:
        """
        Пакетный расчёт изменения за неделю для списка символов.

        Args:
            symbols: Список кодов/символов.
            asset_type: 'currency' или 'crypto'.
            days: Период в днях.

        Returns:
            Словарь {symbol: change_percent}.
        """
        if not symbols:
            return {}

        asset_type = asset_type.lower()
        days = max(1, min(days, 90))
        since = datetime.now(timezone.utc) - timedelta(days=days)

        records = (
            PriceHistory.query
            .filter(
                PriceHistory.asset_type == asset_type,
                PriceHistory.symbol.in_(symbols),
                PriceHistory.recorded_at >= since,
            )
            .order_by(PriceHistory.symbol, PriceHistory.recorded_at.asc())
            .all()
        )

        grouped: Dict[str, List[PriceHistory]] = {}
        for record in records:
            grouped.setdefault(record.symbol, []).append(record)

        # Для USD берём изменение курса RUB (USD/RUB)
        rub_records = []
        if asset_type == 'currency' and 'USD' in symbols:
            rub_records = grouped.get('RUB', [])

        changes: Dict[str, float] = {}
        for symbol in symbols:
            recs = grouped.get(symbol, [])
            if len(recs) < 2:
                changes[symbol] = 0.0
                continue

            if asset_type == 'crypto':
                first_val = float(recs[0].price)
                last_val = float(recs[-1].price)
            elif symbol == 'USD':
                # Изменение USD в рублях = изменение курса RUB
                if len(rub_records) >= 2:
                    first_val = float(rub_records[0].price)
                    last_val = float(rub_records[-1].price)
                else:
                    changes[symbol] = 0.0
                    continue
            else:
                # Для валют считаем изменение стоимости в USD
                first_rate = float(recs[0].price)
                last_rate = float(recs[-1].price)
                if first_rate == 0 or last_rate == 0:
                    changes[symbol] = 0.0
                    continue
                first_val = 1.0 / first_rate
                last_val = 1.0 / last_rate

            if first_val == 0:
                changes[symbol] = 0.0
            else:
                changes[symbol] = round(((last_val - first_val) / first_val) * 100, 2)

        return changes

    @staticmethod
    def get_recent_updates(limit: int = 10) -> List[Dict]:
        """
        Получить последние обновления курсов.

        Args:
            limit: Максимальное количество записей.

        Returns:
            Список последних обновлений.
        """
        records = (
            PriceHistory.query
            .order_by(PriceHistory.recorded_at.desc())
            .limit(limit)
            .all()
        )

        from backend.services.rate_enrichment_service import RateEnrichmentService
        rub_per_usd = RateEnrichmentService.get_rub_per_usd()

        result = []
        for record in records:
            item = record.to_dict()
            price_usd = float(record.price)
            if record.asset_type == 'currency' and record.symbol != 'USD':
                price_usd = 1.0 / price_usd if price_usd else 0
            elif record.asset_type == 'currency' and record.symbol == 'USD':
                price_usd = 1.0

            item['price_usd'] = round(price_usd, 8)
            item['price_rub'] = round(price_usd * rub_per_usd, 2) if rub_per_usd else 0
            result.append(item)

        return result

    @staticmethod
    def get_btc_rub_history(days: int = 7) -> Dict:
        """
        Получить историю BTC/RUB для главной страницы.

        Конвертирует BTC/USD и USD/RUB в BTC/RUB.

        Returns:
            Данные для графика BTC/RUB.
        """
        btc_history = HistoryService.get_history('BTC', 'crypto', days)
        rub_currency = HistoryService.get_history('RUB', 'currency', days)

        if not btc_history.get('history') or not rub_currency.get('history'):
            return {
                'pair': 'BTC/RUB',
                'days': days,
                'history': [],
                'change_percent': 0.0,
                'current_price': None,
                'message': 'Недостаточно данных для построения графика BTC/RUB',
            }

        # Строим карту RUB-курсов по времени (USD -> RUB rate)
        rub_map = {}
        for record in rub_currency['history']:
            timestamp = record['recorded_at'][:16]  # до минут
            rub_map[timestamp] = record['price']

        combined_history = []
        for btc_record in btc_history['history']:
            timestamp = btc_record['recorded_at'][:16]
            rub_rate = rub_map.get(timestamp)

            if rub_rate:
                btc_rub_price = btc_record['price'] * rub_rate
                combined_history.append({
                    'recorded_at': btc_record['recorded_at'],
                    'price': round(btc_rub_price, 2),
                })

        change_percent = 0.0
        if len(combined_history) >= 2:
            first = combined_history[0]['price']
            last = combined_history[-1]['price']
            if first > 0:
                change_percent = round(((last - first) / first) * 100, 2)

        return {
            'pair': 'BTC/RUB',
            'days': days,
            'history': combined_history,
            'change_percent': change_percent,
            'current_price': combined_history[-1]['price'] if combined_history else None,
        }
