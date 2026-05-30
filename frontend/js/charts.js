/**
 * FinRate — Модуль Chart.js графиков (с live-обновлением)
 */
const ChartManager = {
    btcRubChart: null,
    mainChart: null,
    lastBtcData: null,
    lastMainData: null,

    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 600,
        },
        interaction: {
            intersect: false,
            mode: 'index',
        },
        plugins: {
            legend: { display: false },
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
                grid: { color: 'rgba(42, 49, 64, 0.5)' },
                ticks: { color: '#6e7681', maxTicksLimit: 8 },
            },
            y: {
                grid: { color: 'rgba(42, 49, 64, 0.5)' },
                ticks: { color: '#6e7681' },
            },
        },
    },

    renderBtcRubChart(history, changePercent) {
        const canvas = document.getElementById('btcRubChart');
        if (!canvas || !history || history.length === 0) return;

        this.lastBtcData = { history, changePercent };

        const labels = history.map(item => this.formatDate(item.recorded_at));
        const prices = history.map(item => item.price);
        const isPositive = changePercent >= 0;
        const lineColor = isPositive ? '#00c076' : '#f6465d';
        const fillColor = isPositive ? 'rgba(0, 192, 118, 0.12)' : 'rgba(246, 70, 93, 0.12)';

        if (this.btcRubChart) {
            this.btcRubChart.data.labels = labels;
            this.btcRubChart.data.datasets[0].data = prices;
            this.btcRubChart.data.datasets[0].borderColor = lineColor;
            this.btcRubChart.data.datasets[0].backgroundColor = fillColor;
            this.btcRubChart.update('active');
        } else {
            this.btcRubChart = new Chart(canvas.getContext('2d'), {
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
                    }],
                },
                options: {
                    ...this.defaultOptions,
                    plugins: {
                        ...this.defaultOptions.plugins,
                        tooltip: {
                            ...this.defaultOptions.plugins.tooltip,
                            callbacks: {
                                label: (ctx) => `${this.formatPrice(ctx.parsed.y)} ₽`,
                            },
                        },
                    },
                },
            });
        }

        this._updateChangeBadge('btcRubChange', changePercent);
    },

    renderMainChart(title, history, changePercent) {
        const canvas = document.getElementById('mainChart');
        if (!canvas || !history || history.length === 0) return;

        this.lastMainData = { title, history, changePercent };

        const labels = history.map(item => this.formatDate(item.recorded_at));
        const prices = history.map(item => item.price);
        const isPositive = changePercent >= 0;
        const lineColor = isPositive ? '#3861fb' : '#f6465d';
        const fillColor = isPositive ? 'rgba(56, 97, 251, 0.12)' : 'rgba(246, 70, 93, 0.12)';

        if (this.mainChart) {
            this.mainChart.data.labels = labels;
            this.mainChart.data.datasets[0].data = prices;
            this.mainChart.data.datasets[0].label = title;
            this.mainChart.data.datasets[0].borderColor = lineColor;
            this.mainChart.data.datasets[0].backgroundColor = fillColor;
            this.mainChart.update('active');
        } else {
            this.mainChart = new Chart(canvas.getContext('2d'), {
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
                                label: (ctx) => `$${this.formatPrice(ctx.parsed.y)}`,
                            },
                        },
                    },
                },
            });
        }

        const titleEl = document.getElementById('chartTitle');
        if (titleEl) titleEl.textContent = title;
        this._updateChangeBadge('chartChange', changePercent);
    },

    refreshActiveCharts() {
        if (this.lastBtcData) {
            this.renderBtcRubChart(this.lastBtcData.history, this.lastBtcData.changePercent);
        }
        if (this.lastMainData && document.getElementById('section-charts')?.classList.contains('active')) {
            const { title, history, changePercent } = this.lastMainData;
            this.renderMainChart(title, history, changePercent);
        }
    },

    _updateChangeBadge(elementId, changePercent) {
        const el = document.getElementById(elementId);
        if (!el) return;
        el.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent}%`;
        el.className = `change-badge ${changePercent > 0 ? 'positive' : changePercent < 0 ? 'negative' : 'neutral'}`;
    },

    formatDate(isoDate) {
        const date = new Date(isoDate);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
        });
    },

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
