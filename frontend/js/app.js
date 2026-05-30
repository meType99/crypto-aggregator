/**
 * FinRate — Главный модуль приложения
 */
const App = {
    currencies: [],
    cryptos: [],
    refreshTimer: null,
    searchTimer: null,
    refreshInterval: 300,
    isFirstLoad: true,

    async init() {
        this.loadSettings();
        this.bindEvents();
        await this.loadAllData(false);
        this.startAutoRefresh();
        UI.startCountdown(this.refreshInterval);
    },

    async loadAllData(silent = false) {
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn?.classList.add('spinning');

        try {
            const [currenciesRes, cryptoRes, popularCurr, popularCrypto, updatesRes, btcRubRes] =
                await Promise.all([
                    API.getCurrencies(),
                    API.getCrypto(),
                    API.getCurrencies(true),
                    API.getCrypto(true),
                    API.getUpdates(10),
                    API.getBtcRubHistory(7),
                ]);

            this.currencies = currenciesRes.data || [];
            this.cryptos = cryptoRes.data || [];

            const meta = currenciesRes.meta || cryptoRes.meta || {};
            if (meta.refresh_interval) {
                this.refreshInterval = meta.refresh_interval;
            }

            UI.setConnectionStatus(true);
            UI.setLastUpdate(meta.server_time);
            UI.resetCountdown(this.refreshInterval);

            UI.renderCards('currencyCards', popularCurr.data, 'currency');
            UI.renderCards('cryptoCards', popularCrypto.data, 'crypto');

            const activeTab = document.querySelector('.tab-btn.active')?.dataset.table || 'all';
            UI.renderRatesTable(this.currencies, this.cryptos, activeTab);
            UI.renderUpdates(updatesRes.data);

            if (btcRubRes.data && btcRubRes.data.history.length > 0) {
                ChartManager.renderBtcRubChart(
                    btcRubRes.data.history,
                    btcRubRes.data.change_percent
                );
            }

            UI.renderAllCurrencies(this.currencies);
            UI.renderAllCrypto(this.cryptos);

            const assetType = document.getElementById('chartAssetType')?.value || 'crypto';
            UI.populateChartSymbols(this.currencies, this.cryptos, assetType);
            UI.renderFavorites();
            UI.flashUpdatedPrices();

            if (this.isFirstLoad) {
                UI.addNotification('Данные загружены. Автообновление каждые 5 минут.', 'success');
                this.isFirstLoad = false;
            } else if (!silent) {
                UI.addNotification('Курсы обновлены', 'info');
            }
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            UI.setConnectionStatus(false);
            UI.showToast(`Ошибка загрузки: ${error.message}`, 'error');
            UI.addNotification(`Ошибка API: ${error.message}`, 'error');
        } finally {
            refreshBtn?.classList.remove('spinning');
        }
    },

    bindEvents() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                UI.showSection(item.dataset.section);
            });
        });

        document.getElementById('menuToggle')?.addEventListener('click', () => {
            document.getElementById('sidebar')?.classList.toggle('open');
        });

        document.getElementById('refreshBtn')?.addEventListener('click', () => {
            this.loadAllData(false);
        });

        const searchInput = document.getElementById('searchInput');
        searchInput?.addEventListener('input', (e) => {
            clearTimeout(this.searchTimer);
            const query = e.target.value.trim();

            if (query.length < 1) {
                UI.hideSearchResults();
                return;
            }

            this.searchTimer = setTimeout(async () => {
                try {
                    const result = await API.search(query);
                    UI.renderSearchResults(result.data);
                } catch (error) {
                    UI.showToast(`Ошибка поиска: ${error.message}`, 'error');
                }
            }, 300);
        });

        searchInput?.addEventListener('blur', () => {
            setTimeout(() => UI.hideSearchResults(), 200);
        });

        document.getElementById('searchResults')?.addEventListener('click', (e) => {
            const item = e.target.closest('.search-result-item');
            if (!item) return;

            UI.showSection('charts');
            document.getElementById('chartAssetType').value = item.dataset.type;
            UI.populateChartSymbols(this.currencies, this.cryptos, item.dataset.type);
            document.getElementById('chartSymbol').value = item.dataset.symbol;
            this.loadChart();
        });

        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                UI.renderRatesTable(this.currencies, this.cryptos, btn.dataset.table);
            });
        });

        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-favorite')) {
                const symbol = e.target.dataset.symbol;
                const type = e.target.dataset.type;
                const row = e.target.closest('tr');
                const name = row?.querySelector('td:nth-child(2)')?.textContent || symbol;
                UI.toggleFavorite(symbol, type, name);
                e.target.classList.toggle('active');
            }
        });

        document.getElementById('chartAssetType')?.addEventListener('change', (e) => {
            UI.populateChartSymbols(this.currencies, this.cryptos, e.target.value);
        });

        document.getElementById('loadChartBtn')?.addEventListener('click', () => {
            this.loadChart();
        });

        document.getElementById('saveSettingsBtn')?.addEventListener('click', () => {
            this.saveSettings();
            UI.showToast('Настройки сохранены', 'success');
        });
    },

    async loadChart() {
        const symbol = document.getElementById('chartSymbol')?.value;
        const assetType = document.getElementById('chartAssetType')?.value || 'crypto';
        const days = parseInt(document.getElementById('chartDays')?.value || '7', 10);

        if (!symbol) {
            UI.showToast('Выберите актив для графика', 'error');
            return;
        }

        try {
            const result = await API.getHistory(symbol, assetType, days);
            const data = result.data;

            if (!data.history || data.history.length === 0) {
                UI.showToast('Нет исторических данных для этого актива', 'info');
                return;
            }

            ChartManager.renderMainChart(`${symbol}/USD (${days}д)`, data.history, data.change_percent);
        } catch (error) {
            UI.showToast(`Ошибка загрузки графика: ${error.message}`, 'error');
        }
    },

    startAutoRefresh() {
        const autoRefresh = localStorage.getItem('finrate_auto_refresh') !== 'false';
        const interval = parseInt(localStorage.getItem('finrate_refresh_interval') || '300', 10) * 1000;
        this.refreshInterval = interval / 1000;

        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        if (autoRefresh) {
            this.refreshTimer = setInterval(() => this.loadAllData(true), interval);
        }
    },

    loadSettings() {
        const autoRefresh = localStorage.getItem('finrate_auto_refresh') !== 'false';
        const interval = localStorage.getItem('finrate_refresh_interval') || '300';
        const chartDays = localStorage.getItem('finrate_chart_days') || '7';

        document.getElementById('autoRefresh') && (document.getElementById('autoRefresh').checked = autoRefresh);
        document.getElementById('refreshInterval') && (document.getElementById('refreshInterval').value = interval);
        document.getElementById('defaultChartDays') && (document.getElementById('defaultChartDays').value = chartDays);
        document.getElementById('chartDays') && (document.getElementById('chartDays').value = chartDays);

        this.refreshInterval = parseInt(interval, 10);
    },

    saveSettings() {
        const autoRefresh = document.getElementById('autoRefresh')?.checked ?? true;
        const interval = document.getElementById('refreshInterval')?.value || '300';
        const chartDays = document.getElementById('defaultChartDays')?.value || '7';

        localStorage.setItem('finrate_auto_refresh', autoRefresh);
        localStorage.setItem('finrate_refresh_interval', interval);
        localStorage.setItem('finrate_chart_days', chartDays);

        this.refreshInterval = parseInt(interval, 10);
        this.startAutoRefresh();
        UI.resetCountdown(this.refreshInterval);
    },
};

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
