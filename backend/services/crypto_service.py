"""
Сервис получения и хранения курсов криптовалют.
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from flask import current_app

from backend.database.connection import db
from backend.models.cryptocurrency import Cryptocurrency
from backend.models.price_history import PriceHistory
from backend.services.api_client import ApiClient
from backend.services.constants import TRACKED_CRYPTO
from backend.services.rate_enrichment_service import RateEnrichmentService

logger = logging.getLogger(__name__)

# Список отслеживаемых криптовалют: id CoinGecko -> (symbol, name)
# (константа также доступна через constants.TRACKED_CRYPTO)


class CryptoService:
    """Сервис управления криптовалютами."""

    @staticmethod
    def fetch_prices_from_api() -> Optional[Dict[str, float]]:
        """
        Получить актуальные цены криптовалют из CoinGecko API.

        Returns:
            Словарь {symbol: price_usd} или None при ошибке.
        """
        api_url = current_app.config['CRYPTO_API_URL']
        coin_ids = ','.join(TRACKED_CRYPTO.keys())
        params = {
            'ids': coin_ids,
            'vs_currencies': 'usd',
        }

        data = ApiClient.get(api_url, params=params)
        if not data:
            logger.error('Не удалось получить курсы криптовалют из API')
            return None

        prices = {}
        for coin_id, (symbol, _name) in TRACKED_CRYPTO.items():
            if coin_id in data and 'usd' in data[coin_id]:
                prices[symbol] = float(data[coin_id]['usd'])

        if not prices:
            logger.error('API вернул пустой список цен криптовалют')
            return None

        return prices

    @staticmethod
    def update_cryptocurrencies() -> int:
        """
        Обновить цены криптовалют в базе данных.

        Returns:
            Количество обновлённых записей.
        """
        prices = CryptoService.fetch_prices_from_api()
        if not prices:
            return 0

        updated_count = 0
        now = datetime.now(timezone.utc)

        for symbol, price in prices.items():
            coin_info = next(
                (info for info in TRACKED_CRYPTO.values() if info[0] == symbol),
                (symbol, symbol),
            )
            name = coin_info[1]

            crypto = Cryptocurrency.query.filter_by(symbol=symbol).first()

            if crypto:
                crypto.name = name
                crypto.price = Decimal(str(price))
                crypto.updated_at = now
            else:
                crypto = Cryptocurrency(
                    name=name,
                    symbol=symbol,
                    price=Decimal(str(price)),
                    updated_at=now,
                )
                db.session.add(crypto)

            history = PriceHistory(
                asset_type='crypto',
                symbol=symbol,
                price=Decimal(str(price)),
                recorded_at=now,
            )
            db.session.add(history)
            updated_count += 1

        try:
            db.session.commit()
            logger.info('Обновлено %d криптовалют', updated_count)
        except Exception as exc:
            db.session.rollback()
            logger.error('Ошибка сохранения криптовалют в БД: %s', exc)
            return 0

        return updated_count

    @staticmethod
    def get_all() -> List[Dict]:
        """Получить все криптовалюты с USD/RUB и изменением за 7 дней."""
        cryptos = Cryptocurrency.query.order_by(Cryptocurrency.symbol).all()
        return RateEnrichmentService.enrich_cryptos(
            [crypto.to_dict() for crypto in cryptos]
        )

    @staticmethod
    def get_popular(limit: int = 8) -> List[Dict]:
        """Получить популярные криптовалюты."""
        popular_symbols = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE']
        cryptos = (
            Cryptocurrency.query
            .filter(Cryptocurrency.symbol.in_(popular_symbols))
            .all()
        )
        order_map = {sym: idx for idx, sym in enumerate(popular_symbols)}
        cryptos.sort(key=lambda c: order_map.get(c.symbol, 999))
        return RateEnrichmentService.enrich_cryptos(
            [crypto.to_dict() for crypto in cryptos[:limit]]
        )

    @staticmethod
    def search(query: str) -> List[Dict]:
        """Поиск криптовалют по символу или названию."""
        search_term = f'%{query.strip().lower()}%'
        cryptos = (
            Cryptocurrency.query
            .filter(
                db.or_(
                    db.func.lower(Cryptocurrency.symbol).like(search_term),
                    db.func.lower(Cryptocurrency.name).like(search_term),
                )
            )
            .order_by(Cryptocurrency.symbol)
            .limit(50)
            .all()
        )
        return RateEnrichmentService.enrich_cryptos(
            [crypto.to_dict() for crypto in cryptos]
        )

    @staticmethod
    def get_by_symbol(symbol: str) -> Optional[Dict]:
        """Получить криптовалюту по символу."""
        crypto = Cryptocurrency.query.filter_by(symbol=symbol.upper()).first()
        return RateEnrichmentService.enrich_crypto(
            crypto.to_dict() if crypto else None
        )
