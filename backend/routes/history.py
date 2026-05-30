"""
Маршрут GET /api/history — история изменения курса.
"""
import logging

from flask import Blueprint, jsonify, request

from backend.services.history_service import HistoryService

logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
def get_history():
    """
    Получить историю изменения курса для графиков.

    Query-параметры:
        symbol (str): Код валюты или символ криптовалюты (обязательный).
        type (str): Тип актива — currency или crypto (по умолчанию crypto).
        days (int): Количество дней истории (по умолчанию 7, макс. 90).
        pair (str): Специальная пара, например btc_rub.
    """
    try:
        pair = request.args.get('pair', '').lower()

        if pair == 'btc_rub':
            days = request.args.get('days', 7, type=int)
            data = HistoryService.get_btc_rub_history(days)
            return jsonify({
                'success': True,
                'data': data,
            })

        symbol = request.args.get('symbol', '').strip()
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Параметр symbol обязателен',
            }), 400

        asset_type = request.args.get('type', 'crypto')
        days = request.args.get('days', 7, type=int)

        data = HistoryService.get_history(symbol, asset_type, days)

        if 'error' in data:
            return jsonify({
                'success': False,
                'error': data['error'],
            }), 400

        return jsonify({
            'success': True,
            'data': data,
        })
    except Exception as exc:
        logger.error('Ошибка GET /api/history: %s', exc)
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера при получении истории',
        }), 500
