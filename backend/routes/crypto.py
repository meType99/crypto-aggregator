"""
Маршрут GET /api/crypto — список криптовалют.
"""
import logging

from flask import Blueprint, jsonify, request

from backend.services.crypto_service import CryptoService
from backend.services.rate_enrichment_service import RateEnrichmentService

logger = logging.getLogger(__name__)

crypto_bp = Blueprint('crypto', __name__)


@crypto_bp.route('/crypto', methods=['GET'])
def get_crypto():
    """
    Получить список всех криптовалют или популярных.

    Query-параметры:
        popular (bool): Если true — только популярные криптовалюты.
        symbol (str): Получить одну криптовалюту по символу.
    """
    try:
        symbol = request.args.get('symbol')
        if symbol:
            crypto = CryptoService.get_by_symbol(symbol)
            if not crypto:
                return jsonify({
                    'success': False,
                    'error': f'Криптовалюта {symbol} не найдена',
                }), 404
            return jsonify({
                'success': True,
                'data': crypto,
            })

        popular = request.args.get('popular', 'false').lower() == 'true'
        if popular:
            data = CryptoService.get_popular()
        else:
            data = CryptoService.get_all()

        return jsonify({
            'success': True,
            'meta': RateEnrichmentService.get_meta(),
            'count': len(data),
            'data': data,
        })
    except Exception as exc:
        logger.error('Ошибка GET /api/crypto: %s', exc)
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера при получении криптовалют',
        }), 500
