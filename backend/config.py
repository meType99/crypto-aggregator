"""
Конфигурация приложения Flask.
Настройки загружаются из переменных окружения с разумными значениями по умолчанию.
"""
import os
from pathlib import Path

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DEFAULT_SQLITE_PATH = DATA_DIR / 'currency_aggregator.db'


class Config:
    """Базовый класс конфигурации."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # SQLite (файл создаётся автоматически при первом запуске)
    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(DEFAULT_SQLITE_PATH))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + Path(DATABASE_PATH).as_posix()
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False},
        'pool_pre_ping': True,
    }

    # Интервал автоматического обновления курсов (в секундах)
    UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 300))

    # Внешние API
    CURRENCY_API_URL = os.environ.get(
        'CURRENCY_API_URL',
        'https://open.er-api.com/v6/latest/USD'
    )
    CRYPTO_API_URL = os.environ.get(
        'CRYPTO_API_URL',
        'https://api.coingecko.com/api/v3/simple/price'
    )

    # Логирование
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    # Путь к frontend
    FRONTEND_FOLDER = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'frontend')
    )
