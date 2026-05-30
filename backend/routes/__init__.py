"""
Регистрация маршрутов REST API.
"""
from backend.routes.currencies import currencies_bp
from backend.routes.crypto import crypto_bp
from backend.routes.search import search_bp
from backend.routes.history import history_bp
from backend.routes.updates import updates_bp


def register_routes(app):
    """
    Зарегистрировать все blueprint-маршруты в приложении.

    Args:
        app: Экземпляр Flask-приложения.
    """
    app.register_blueprint(currencies_bp, url_prefix='/api')
    app.register_blueprint(crypto_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(updates_bp, url_prefix='/api')
