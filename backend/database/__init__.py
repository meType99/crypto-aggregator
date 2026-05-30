"""
Модуль инициализации базы данных.
Экспортирует экземпляр SQLAlchemy для использования в моделях и сервисах.
"""
from backend.database.connection import db, init_db

__all__ = ['db', 'init_db']
