"""
Маршрут GET /api/currencies — список фиатных валют.
"""
import logging

from flask import Blueprint, jsonify, request

from backend.services.currency_service import CurrencyService
from backend.services.rate_enrichment_service import RateEnrichmentService

logger = logging.getLogger(__name__)

currencies_bp = Blueprint('currencies', __name__)


@currencies_bp.route('/currencies', methods=['GET'])
def get_currencies():
    """
    Получить список всех валют или популярных валют.

    Query-параметры:
        popular (bool): Если true — только популярные валюты.
        code (str): Получить одну валюту по коду.
    """
    try:
        code = request.args.get('code')
        if code:
            currency = CurrencyService.get_by_code(code)
            if not currency:
                return jsonify({
                    'success': False,
                    'error': f'Валюта с кодом {code} не найдена',
                }), 404
            return jsonify({
                'success': True,
                'data': currency,
            })

        popular = request.args.get('popular', 'false').lower() == 'true'
        if popular:
            data = CurrencyService.get_popular()
        else:
            data = CurrencyService.get_all()

        return jsonify({
            'success': True,
            'meta': RateEnrichmentService.get_meta(),
            'count': len(data),
            'data': data,
        })
    except Exception as exc:
        logger.error('Ошибка GET /api/currencies: %s', exc)
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера при получении валют',
        }), 500
