/**
 * FinRate — Модуль Chart.js графиков
 */
const ChartManager = {
    btcRubChart: null,
    mainChart: null,

    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index',
        },
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                backgroundColor: '#1a1f27',
                titleColor: '#e8eaed',
                bodyColor: '#8b949e',
                borderColor: '#2a3140',
                borderWidth: 1,
                padding: 12,
                displayColors: false,
            },
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(42, 49, 64, 0.5)',
                },
                ticks: {
                    color: '#6e7681',
                    maxTicksLimit: 8,
                },
            },
            y: {
                grid: {
                    color: 'rgba(42, 49, 64, 0.5)',
                },
                ticks: {
                    color: '#6e7681',
                },
            },
        },
    },

    /**
     * Построить график BTC/RUB на главной странице.
     * @param {Array} history - Массив записей истории.
     * @param {number} changePercent - Процент изменения.
     */
    renderBtcRubChart(history, changePercent) {
        const canvas = document.getElementById('btcRubChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const labels = history.map(item => this.formatDate(item.recorded_at));
        const prices = history.map(item => item.price);

        const isPositive = changePercent >= 0;
        const lineColor = isPositive ? '#00c076' : '#f6465d';
        const fillColor = isPositive
            ? 'rgba(0, 192, 118, 0.1)'
            : 'rgba(246, 70, 93, 0.1)';

        if (this.btcRubChart) {
            this.btcRubChart.destroy();
        }

        this.btcRubChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'BTC/RUB',
                    data: prices,
                    borderColor: lineColor,
                    backgroundColor: fillColor,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: lineColor,
                }],
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: (context) => {
                                return `${this.formatPrice(context.parsed.y)} ₽`;
                            },
                        },
                    },
                },
            },
        });

        const changeEl = document.getElementById('btcRubChange');
        if (changeEl) {
            changeEl.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent}%`;
            changeEl.className = `change-badge ${changePercent > 0 ? 'positive' : changePercent < 0 ? 'negative' : 'neutral'}`;
        }
    },

    /**
     * Построить основной график на странице «Графики».
     * @param {string} title - Заголовок графика.
     * @param {Array} history - Данные истории.
     * @param {number} changePercent - Процент изменения.
     */
    renderMainChart(title, history, changePercent) {
        const canvas = document.getElementById('mainChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const labels = history.map(item => this.formatDate(item.recorded_at));
        const prices = history.map(item => item.price);

        const isPositive = changePercent >= 0;
        const lineColor = isPositive ? '#3861fb' : '#f6465d';
        const fillColor = isPositive
            ? 'rgba(56, 97, 251, 0.1)'
            : 'rgba(246, 70, 93, 0.1)';

        if (this.mainChart) {
            this.mainChart.destroy();
        }

        this.mainChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: title,
                    data: prices,
                    borderColor: lineColor,
                    backgroundColor: fillColor,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: history.length <= 30 ? 3 : 0,
                    pointHoverRadius: 6,
                }],
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: (context) => {
                                return `$${this.formatPrice(context.parsed.y)}`;
                            },
                        },
                    },
                },
            },
        });

        const titleEl = document.getElementById('chartTitle');
        const changeEl = document.getElementById('chartChange');

        if (titleEl) titleEl.textContent = title;
        if (changeEl) {
            changeEl.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent}%`;
            changeEl.className = `change-badge ${changePercent > 0 ? 'positive' : changePercent < 0 ? 'negative' : 'neutral'}`;
        }
    },

    /**
     * Форматировать дату для оси X.
     * @param {string} isoDate - ISO-строка даты.
     */
    formatDate(isoDate) {
        const date = new Date(isoDate);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
        });
    },

    /**
     * Форматировать цену.
     * @param {number} price - Числовое значение.
     */
    formatPrice(price) {
        if (price >= 1000) {
            return price.toLocaleString('ru-RU', { maximumFractionDigits: 2 });
        }
        if (price >= 1) {
            return price.toLocaleString('ru-RU', { maximumFractionDigits: 4 });
        }
        return price.toLocaleString('ru-RU', { maximumFractionDigits: 8 });
    },
};
