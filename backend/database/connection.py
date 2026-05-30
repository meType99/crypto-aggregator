"""
Подключение к SQLite через SQLAlchemy.
"""
import logging
import os

from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

db = SQLAlchemy()


def init_db(app):
    """
    Инициализация базы данных и создание таблиц.

    Args:
        app: Экземпляр Flask-приложения.
    """
    db.init_app(app)

    # Создаём папку data/ для файла SQLite
    db_path = app.config.get('DATABASE_PATH')
    if db_path:
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info('Создана директория для БД: %s', db_dir)

    with app.app_context():
        try:
            db.create_all()
            logger.info('Таблицы SQLite успешно созданы или уже существуют.')
        except Exception as exc:
            logger.error('Ошибка при создании таблиц БД: %s', exc)
            raise
