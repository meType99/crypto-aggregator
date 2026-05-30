/**
 * FinRate — Модуль REST API клиента
 */
const API = {
    BASE_URL: '/api',

    /**
     * Выполнить GET-запрос к API.
     * @param {string} endpoint - Путь эндпоинта.
     * @param {Object} params - Query-параметры.
     * @returns {Promise<Object>} JSON-ответ.
     */
    async get(endpoint, params = {}) {
        const url = new URL(`${this.BASE_URL}${endpoint}`, window.location.origin);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                url.searchParams.append(key, value);
            }
        });

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        return data;
    },

    /**
     * Получить список валют.
     * @param {boolean} popular - Только популярные.
     */
    async getCurrencies(popular = false) {
        return this.get('/currencies', { popular: popular ? 'true' : undefined });
    },

    /**
     * Получить список криптовалют.
     * @param {boolean} popular - Только популярные.
     */
    async getCrypto(popular = false) {
        return this.get('/crypto', { popular: popular ? 'true' : undefined });
    },

    /**
     * Поиск активов.
     * @param {string} query - Строка поиска.
     */
    async search(query) {
        return this.get('/search', { q: query });
    },

    /**
     * Получить историю курса.
     * @param {string} symbol - Символ актива.
     * @param {string} type - Тип: currency | crypto.
     * @param {number} days - Количество дней.
     */
    async getHistory(symbol, type = 'crypto', days = 7) {
        return this.get('/history', { symbol, type, days });
    },

    /**
     * Получить историю BTC/RUB.
     * @param {number} days - Количество дней.
     */
    async getBtcRubHistory(days = 7) {
        return this.get('/history', { pair: 'btc_rub', days });
    },

    /**
     * Получить последние обновления.
     * @param {number} limit - Количество записей.
     */
    async getUpdates(limit = 10) {
        return this.get('/updates', { limit });
    },
};
