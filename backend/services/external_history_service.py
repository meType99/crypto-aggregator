"""
Загрузка истории курсов из внешних API (CoinGecko, Frankfurter).
Используется когда в SQLite ещё мало данных (например, после деплоя на Render).
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from flask import current_app

from backend.services.api_client import ApiClient
from backend.services.constants import SYMBOL_TO_COINGECKO, TRACKED_CRYPTO

logger = logging.getLogger(__name__)

# Валюты, поддерживаемые Frankfurter (ECB)
FRANKFURTER_CURRENCIES = {
    'EUR', 'GBP', 'JPY', 'CNY', 'RUB', 'CHF', 'CAD', 'AUD', 'KRW', 'INR',
    'BRL', 'TRY', 'PLN', 'SEK', 'NOK', 'DKK', 'CZK', 'HUF', 'RON', 'BGN',
    'HRK', 'ISK', 'MXN', 'SGD', 'HKD', 'NZD', 'ZAR', 'THB', 'MYR', 'PHP',
    'IDR', 'ILS',
}


class ExternalHistoryService:
    """Получение истории и % изменения из открытых API."""

    @staticmethod
    def _coingecko_base() -> str:
        """Базовый URL CoinGecko API v3."""
        url = current_app.config.get('CRYPTO_API_URL', '')
        if '/simple' in url:
            return url.split('/simple')[0]
        return 'https://api.coingecko.com/api/v3'

    @staticmethod
    def _date_range(days: int) -> Tuple[str, str]:
        # Frankfurter публикует курсы с задержкой — берём вчера как конец периода
        end = datetime.now(timezone.utc).date() - timedelta(days=1)
        start = end - timedelta(days=days)
        return start.isoformat(), end.isoformat()

    @staticmethod
    def get_crypto_weekly_changes() -> Dict[str, float]:
        """
        Получить % изменения за 7 дней для всех криптовалют (один запрос).
        """
        coin_ids = ','.join(TRACKED_CRYPTO.keys())
        url = f'{ExternalHistoryService._coingecko_base()}/coins/markets'
        params = {
            'vs_currency': 'usd',
            'ids': coin_ids,
            'price_change_percentage': '7d',
            'sparkline': 'false',
        }

        data = ApiClient.get(url, params=params)
        if not data:
            return {}

        changes = {}
        for item in data:
            symbol = item.get('symbol', '').upper()
            change = item.get('price_change_percentage_7d')
            if symbol and change is not None:
                changes[symbol] = round(float(change), 2)

        return changes

    @staticmethod
    def get_currency_weekly_changes(symbols: List[str], days: int = 7) -> Dict[str, float]:
        """
        % изменения за период для фиатных валют через Frankfurter API.
        """
        codes = [s for s in symbols if s in FRANKFURTER_CURRENCIES and s != 'USD']
        changes: Dict[str, float] = {}

        if not codes:
            return changes

        start, end = ExternalHistoryService._date_range(days)
        url = f'https://api.frankfurter.app/{start}..{end}'
        params = {'from': 'USD', 'to': ','.join(codes)}

        data = ApiClient.get(url, params=params)
        if not data or 'rates' not in data:
            return changes

        rates_by_date = data['rates']
        dates = sorted(rates_by_date.keys())
        if len(dates) < 2:
            return changes

        first_rates = rates_by_date[dates[0]]
        last_rates = rates_by_date[dates[-1]]

        for code in codes:
            if code not in first_rates or code not in last_rates:
                continue
            first_rate = float(first_rates[code])
            last_rate = float(last_rates[code])
            if first_rate == 0 or last_rate == 0:
                continue
            first_usd = 1.0 / first_rate
            last_usd = 1.0 / last_rate
            changes[code] = round(((last_usd - first_usd) / first_usd) * 100, 2)

        # USD — изменение через RUB
        if 'USD' in symbols and 'RUB' in changes:
            rub_start = float(first_rates.get('RUB', 0))
            rub_end = float(last_rates.get('RUB', 0))
            if rub_start > 0:
                changes['USD'] = round(((rub_end - rub_start) / rub_start) * 100, 2)
        elif 'USD' in symbols and 'RUB' in first_rates and 'RUB' in last_rates:
            rub_start = float(first_rates['RUB'])
            rub_end = float(last_rates['RUB'])
            if rub_start > 0:
                changes['USD'] = round(((rub_end - rub_start) / rub_start) * 100, 2)

        return changes

    @staticmethod
    def get_crypto_history(symbol: str, days: int = 7) -> List[Dict]:
        """История цены криптовалюты в USD из CoinGecko."""
        coin_id = SYMBOL_TO_COINGECKO.get(symbol.upper())
        if not coin_id:
            return []

        base_url = ExternalHistoryService._coingecko_base()
        url = f'{base_url}/coins/{coin_id}/market_chart'
        params = {'vs_currency': 'usd', 'days': str(days)}

        data = ApiClient.get(url, params=params)
        if not data or 'prices' not in data:
            return []

        history = []
        for ts_ms, price in data['prices']:
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            history.append({
                'recorded_at': dt.isoformat(),
                'price': round(float(price), 8),
            })

        return history

    @staticmethod
    def get_currency_history(symbol: str, days: int = 7) -> List[Dict]:
        """История курса валюты из Frankfurter (курс к USD)."""
        code = symbol.upper()
        if code not in FRANKFURTER_CURRENCIES:
            return []

        start, end = ExternalHistoryService._date_range(days)
        url = f'https://api.frankfurter.app/{start}..{end}'
        params = {'from': 'USD', 'to': code}

        data = ApiClient.get(url, params=params)
        if not data or 'rates' not in data:
            return []

        history = []
        for date_str, rates in sorted(data['rates'].items()):
            if code in rates:
                dt = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                history.append({
                    'recorded_at': dt.isoformat(),
                    'price': round(float(rates[code]), 8),
                })

        return history

    @staticmethod
    def get_btc_rub_history(days: int = 7) -> List[Dict]:
        """История BTC/RUB напрямую из CoinGecko."""
        base_url = ExternalHistoryService._coingecko_base()
        url = f'{base_url}/coins/bitcoin/market_chart'
        params = {'vs_currency': 'rub', 'days': str(days)}

        data = ApiClient.get(url, params=params)
        if not data or 'prices' not in data:
            return []

        history = []
        for ts_ms, price in data['prices']:
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            history.append({
                'recorded_at': dt.isoformat(),
                'price': round(float(price), 2),
            })

        return history

    @staticmethod
    def calculate_change(history: List[Dict]) -> float:
        """Рассчитать % изменения по истории."""
        if len(history) < 2:
            return 0.0
        first = history[0]['price']
        last = history[-1]['price']
        if first == 0:
            return 0.0
        return round(((last - first) / first) * 100, 2)

    @staticmethod
    def merge_weekly_changes(
        local: Dict[str, float],
        symbols: List[str],
        asset_type: str,
    ) -> Dict[str, float]:
        """
        Объединить локальные и внешние % изменения.
        Внешние API приоритетнее — сразу работает после деплоя.
        """
        result = dict(local)

        if asset_type == 'crypto':
            external = ExternalHistoryService.get_crypto_weekly_changes()
            for sym in symbols:
                if sym in external:
                    result[sym] = external[sym]
        else:
            external = ExternalHistoryService.get_currency_weekly_changes(symbols)
            for sym in symbols:
                if sym in external:
                    result[sym] = external[sym]

        return result
