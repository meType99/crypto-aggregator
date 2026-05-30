"""
Маршрут GET /api/search — поиск валют и криптовалют.
"""
import logging

from flask import Blueprint, jsonify, request

from backend.services.search_service import SearchService

logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['GET'])
def search():
    """
    Поиск по валютам и криптовалютам.

    Query-параметры:
        q (str): Строка поиска (обязательный).
    """
    try:
        query = request.args.get('q', '').strip()

        if not query:
            return jsonify({
                'success': False,
                'error': 'Параметр q (строка поиска) обязателен',
            }), 400

        if len(query) < 1:
            return jsonify({
                'success': False,
                'error': 'Строка поиска слишком короткая',
            }), 400

        results = SearchService.search(query)

        return jsonify({
            'success': True,
            'query': query,
            'total': results['total'],
            'data': {
                'currencies': results['currencies'],
                'cryptocurrencies': results['cryptocurrencies'],
            },
        })
    except Exception as exc:
        logger.error('Ошибка GET /api/search: %s', exc)
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера при поиске',
        }), 500
