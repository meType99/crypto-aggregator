"""
Сервис объединённого поиска по валютам и криптовалютам.
"""
from typing import Dict, List

from backend.services.crypto_service import CryptoService
from backend.services.currency_service import CurrencyService


class SearchService:
    """Сервис поиска активов."""

    @staticmethod
    def search(query: str) -> Dict[str, List[Dict]]:
        """
        Поиск по валютам и криптовалютам одновременно.

        Args:
            query: Строка поиска.

        Returns:
            Словарь с результатами по типам активов.
        """
        if not query or not query.strip():
            return {
                'currencies': [],
                'cryptocurrencies': [],
                'total': 0,
            }

        currencies = CurrencyService.search(query)
        cryptos = CryptoService.search(query)

        return {
            'currencies': currencies,
            'cryptocurrencies': cryptos,
            'total': len(currencies) + len(cryptos),
        }
