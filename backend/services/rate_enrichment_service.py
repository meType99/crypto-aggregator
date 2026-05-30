"""
Сервис обогащения данных: USD/RUB и изменение за 7 дней.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.models.currency import Currency
from backend.services.history_service import HistoryService


class RateEnrichmentService:
    """Добавляет курс в рублях и процент изменения за неделю."""

    REFRESH_INTERVAL = 300  # секунд — синхронно с backend

    @staticmethod
    def get_rub_per_usd() -> float:
        """Курс USD/RUB (сколько рублей за 1 доллар)."""
        rub = Currency.query.filter_by(code='RUB').first()
        return float(rub.rate) if rub and rub.rate else 0.0

    @staticmethod
    def currency_usd_value(code: str, rate: float) -> float:
        """Стоимость 1 единицы валюты в USD."""
        if code == 'USD':
            return 1.0
        if not rate:
            return 0.0
        return 1.0 / rate

    @staticmethod
    def enrich_currencies(currencies: List[Dict]) -> List[Dict]:
        """Обогатить список валют: rate_usd, rate_rub, change_percent_7d."""
        if not currencies:
            return []

        rub_per_usd = RateEnrichmentService.get_rub_per_usd()
        symbols = [c['code'] for c in currencies]
        changes = HistoryService.get_weekly_changes_batch(symbols, 'currency')

        enriched = []
        for item in currencies:
            code = item['code']
            rate = item['rate']
            rate_usd = RateEnrichmentService.currency_usd_value(code, rate)
            rate_rub = rate_usd * rub_per_usd if rub_per_usd else 0.0

            enriched.append({
                **item,
                'rate_usd': round(rate_usd, 8),
                'rate_rub': round(rate_rub, 4),
                'change_percent_7d': changes.get(code, 0.0),
            })
        return enriched

    @staticmethod
    def enrich_cryptos(cryptos: List[Dict]) -> List[Dict]:
        """Обогатить список криптовалют: price_usd, price_rub, change_percent_7d."""
        if not cryptos:
            return []

        rub_per_usd = RateEnrichmentService.get_rub_per_usd()
        symbols = [c['symbol'] for c in cryptos]
        changes = HistoryService.get_weekly_changes_batch(symbols, 'crypto')

        enriched = []
        for item in cryptos:
            price_usd = item['price']
            price_rub = price_usd * rub_per_usd if rub_per_usd else 0.0

            enriched.append({
                **item,
                'price_usd': round(price_usd, 8),
                'price_rub': round(price_rub, 2),
                'change_percent_7d': changes.get(item['symbol'], 0.0),
            })
        return enriched

    @staticmethod
    def enrich_currency(item: Optional[Dict]) -> Optional[Dict]:
        """Обогатить одну валюту."""
        if not item:
            return None
        return RateEnrichmentService.enrich_currencies([item])[0]

    @staticmethod
    def enrich_crypto(item: Optional[Dict]) -> Optional[Dict]:
        """Обогатить одну криптовалюту."""
        if not item:
            return None
        return RateEnrichmentService.enrich_cryptos([item])[0]

    @staticmethod
    def get_meta() -> Dict:
        """Мета-информация для frontend (real-time)."""
        return {
            'rub_per_usd': RateEnrichmentService.get_rub_per_usd(),
            'server_time': datetime.now(timezone.utc).isoformat(),
            'refresh_interval': RateEnrichmentService.REFRESH_INTERVAL,
        }
