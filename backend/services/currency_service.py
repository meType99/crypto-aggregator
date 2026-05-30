"""
Сервис получения и хранения курсов фиатных валют.
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from flask import current_app

from backend.database.connection import db
from backend.models.currency import Currency
from backend.models.price_history import PriceHistory
from backend.services.api_client import ApiClient

logger = logging.getLogger(__name__)

# Справочник названий популярных валют
CURRENCY_NAMES: Dict[str, str] = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'CNY': 'Chinese Yuan',
    'RUB': 'Russian Ruble',
    'CHF': 'Swiss Franc',
    'CAD': 'Canadian Dollar',
    'AUD': 'Australian Dollar',
    'KRW': 'South Korean Won',
    'INR': 'Indian Rupee',
    'BRL': 'Brazilian Real',
    'TRY': 'Turkish Lira',
    'PLN': 'Polish Zloty',
    'UAH': 'Ukrainian Hryvnia',
    'KZT': 'Kazakhstani Tenge',
    'AED': 'UAE Dirham',
    'SGD': 'Singapore Dollar',
    'HKD': 'Hong Kong Dollar',
    'SEK': 'Swedish Krona',
}


from backend.services.rate_enrichment_service import RateEnrichmentService


class CurrencyService:
    """Сервис управления фиатными валютами."""

    @staticmethod
    def fetch_rates_from_api() -> Optional[Dict[str, float]]:
        """
        Получить актуальные курсы валют из внешнего API.

        Returns:
            Словарь {код_валюты: курс} или None при ошибке.
        """
        api_url = current_app.config['CURRENCY_API_URL']
        data = ApiClient.get(api_url)

        if not data or data.get('result') != 'success':
            logger.error('Не удалось получить курсы валют из API')
            return None

        rates = data.get('rates', {})
        if not rates:
            logger.error('API вернул пустой список курсов валют')
            return None

        return {code: float(rate) for code, rate in rates.items()}

    @staticmethod
    def update_currencies() -> int:
        """
        Обновить курсы валют в базе данных из внешнего API.

        Returns:
            Количество обновлённых записей.
        """
        rates = CurrencyService.fetch_rates_from_api()
        if not rates:
            return 0

        updated_count = 0
        now = datetime.now(timezone.utc)

        for code, rate in rates.items():
            name = CURRENCY_NAMES.get(code, code)
            currency = Currency.query.filter_by(code=code).first()

            if currency:
                currency.name = name
                currency.rate = Decimal(str(rate))
                currency.updated_at = now
            else:
                currency = Currency(
                    name=name,
                    code=code,
                    rate=Decimal(str(rate)),
                    updated_at=now,
                )
                db.session.add(currency)

            # Сохраняем историю для построения графиков
            history = PriceHistory(
                asset_type='currency',
                symbol=code,
                price=Decimal(str(rate)),
                recorded_at=now,
            )
            db.session.add(history)
            updated_count += 1

        try:
            db.session.commit()
            logger.info('Обновлено %d валют', updated_count)
        except Exception as exc:
            db.session.rollback()
            logger.error('Ошибка сохранения валют в БД: %s', exc)
            return 0

        return updated_count

    @staticmethod
    def get_all() -> List[Dict]:
        """Получить все валюты из БД с USD/RUB и изменением за 7 дней."""
        currencies = Currency.query.order_by(Currency.code).all()
        return RateEnrichmentService.enrich_currencies(
            [currency.to_dict() for currency in currencies]
        )

    @staticmethod
    def get_popular(limit: int = 8) -> List[Dict]:
        """Получить популярные валюты."""
        popular_codes = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'RUB', 'CHF', 'CAD']
        currencies = (
            Currency.query
            .filter(Currency.code.in_(popular_codes))
            .all()
        )
        order_map = {code: idx for idx, code in enumerate(popular_codes)}
        currencies.sort(key=lambda c: order_map.get(c.code, 999))
        return RateEnrichmentService.enrich_currencies(
            [currency.to_dict() for currency in currencies[:limit]]
        )

    @staticmethod
    def search(query: str) -> List[Dict]:
        """Поиск валют по коду или названию."""
        search_term = f'%{query.strip().lower()}%'
        currencies = (
            Currency.query
            .filter(
                db.or_(
                    db.func.lower(Currency.code).like(search_term),
                    db.func.lower(Currency.name).like(search_term),
                )
            )
            .order_by(Currency.code)
            .limit(50)
            .all()
        )
        return RateEnrichmentService.enrich_currencies(
            [currency.to_dict() for currency in currencies]
        )

    @staticmethod
    def get_by_code(code: str) -> Optional[Dict]:
        """Получить валюту по коду."""
        currency = Currency.query.filter_by(code=code.upper()).first()
        return RateEnrichmentService.enrich_currency(
            currency.to_dict() if currency else None
        )
