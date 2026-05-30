"""
Точка входа Flask-приложения «Агрегатор курсов валют и криптовалют».
"""
import os
import sys

# Добавляем корень проекта в PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.database.connection import init_db
from backend.routes import register_routes
from backend.services.updater_service import DataUpdater
from backend.utils.logger import setup_logging


def create_app(config_class=Config):
    """
    Фабрика Flask-приложения.

    Args:
        config_class: Класс конфигурации.

    Returns:
        Настроенный экземпляр Flask.
    """
    app = Flask(
        __name__,
        static_folder=config_class.FRONTEND_FOLDER,
        static_url_path='',
    )
    app.config.from_object(config_class)

    # CORS для REST API
    CORS(app, resources={r'/api/*': {'origins': app.config['CORS_ORIGINS']}})

    # Логирование
    setup_logging(app)

    # База данных
    init_db(app)

    # Маршруты API
    register_routes(app)

    # Раздача frontend-файлов
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    # Фоновое обновление данных
    updater = DataUpdater(app, interval=app.config['UPDATE_INTERVAL'])
    app.updater = updater

    def start_background_tasks():
        """Первичная загрузка и запуск автообновления."""
        if getattr(app, '_background_started', False):
            return
        app._background_started = True
        try:
            updater.update_now()
            updater.start()
            app.logger.info('Фоновые задачи обновления данных запущены')
        except Exception as exc:
            app.logger.error('Ошибка запуска фоновых задач: %s', exc)

    app.start_background_tasks = start_background_tasks

    return app


app = create_app()

# Запуск фонового обновления при старте приложения
with app.app_context():
    app.start_background_tasks()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'true').lower() == 'true',
    )
