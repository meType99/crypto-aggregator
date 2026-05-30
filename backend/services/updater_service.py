"""
Фоновое автоматическое обновление курсов валют и криптовалют.
"""
import logging
from threading import Event, Thread

from flask import Flask

logger = logging.getLogger(__name__)


class DataUpdater:
    """Планировщик периодического обновления данных из внешних API."""

    def __init__(self, app: Flask, interval: int = 300):
        """
        Args:
            app: Экземпляр Flask-приложения.
            interval: Интервал обновления в секундах.
        """
        self.app = app
        self.interval = interval
        self._stop_event = Event()
        self._thread = None

    def start(self):
        """Запустить фоновый поток обновления."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(
            'Фоновое обновление данных запущено (интервал: %d сек)',
            self.interval,
        )

    def stop(self):
        """Остановить фоновый поток."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info('Фоновое обновление данных остановлено')

    def _run(self):
        """Основной цикл обновления."""
        while not self._stop_event.is_set():
            self._update_all()
            self._stop_event.wait(self.interval)

    def _update_all(self):
        """Обновить все данные в контексте приложения."""
        with self.app.app_context():
            from backend.services.currency_service import CurrencyService
            from backend.services.crypto_service import CryptoService

            try:
                currency_count = CurrencyService.update_currencies()
                crypto_count = CryptoService.update_cryptocurrencies()
                logger.info(
                    'Автообновление завершено: %d валют, %d криптовалют',
                    currency_count,
                    crypto_count,
                )
            except Exception as exc:
                logger.error('Ошибка автообновления данных: %s', exc)

    def update_now(self):
        """Немедленное обновление данных."""
        self._update_all()
