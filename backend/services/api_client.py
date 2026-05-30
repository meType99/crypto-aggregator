"""
Сервис для работы с внешними API и логирования ошибок.
"""
import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class ApiClient:
    """HTTP-клиент для запросов к внешним API с обработкой ошибок."""

    DEFAULT_TIMEOUT = 15

    @staticmethod
    def get(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Выполнить GET-запрос к внешнему API.

        Args:
            url: URL запроса.
            params: Query-параметры.

        Returns:
            JSON-ответ или None при ошибке.
        """
        try:
            response = requests.get(
                url,
                params=params,
                timeout=ApiClient.DEFAULT_TIMEOUT,
                headers={'Accept': 'application/json'},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error('Таймаут при запросе к API: %s', url)
        except requests.exceptions.HTTPError as exc:
            logger.error(
                'HTTP-ошибка API %s: статус %s, ответ: %s',
                url,
                exc.response.status_code if exc.response else 'N/A',
                exc.response.text[:500] if exc.response else 'N/A',
            )
        except requests.exceptions.ConnectionError:
            logger.error('Ошибка соединения с API: %s', url)
        except requests.exceptions.RequestException as exc:
            logger.error('Ошибка запроса к API %s: %s', url, exc)
        except ValueError:
            logger.error('Некорректный JSON в ответе API: %s', url)

        return None
