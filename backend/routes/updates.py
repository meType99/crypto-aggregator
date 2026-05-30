"""
Маршрут GET /api/updates — последние обновления курсов.
"""
import logging

from flask import Blueprint, jsonify, request

from backend.services.history_service import HistoryService

logger = logging.getLogger(__name__)

updates_bp = Blueprint('updates', __name__)


@updates_bp.route('/updates', methods=['GET'])
def get_updates():
    """
    Получить блок последних обновлений курсов.

    Query-параметры:
        limit (int): Количество записей (по умолчанию 10).
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = max(1, min(limit, 50))

        data = HistoryService.get_recent_updates(limit)

        return jsonify({
            'success': True,
            'count': len(data),
            'data': data,
        })
    except Exception as exc:
        logger.error('Ошибка GET /api/updates: %s', exc)
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера',
        }), 500
