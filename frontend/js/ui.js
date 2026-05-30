/**
 * FinRate — Модуль UI-компонентов и утилит
 */
const UI = {
    favorites: JSON.parse(localStorage.getItem('finrate_favorites') || '[]'),
    countdownTimer: null,
    secondsToRefresh: 300,

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    },

    addNotification(text, type = 'info') {
        const list = document.getElementById('notificationsList');
        if (!list) return;

        const item = document.createElement('li');
        item.className = `notification-item ${type}`;
        item.innerHTML = `
            <span class="notification-time">${new Date().toLocaleTimeString('ru-RU')}</span>
            <span class="notification-text">${text}</span>
        `;
        list.prepend(item);

        while (list.children.length > 20) {
            list.removeChild(list.lastChild);
        }
    },

    setConnectionStatus(online) {
        const dot = document.getElementById('statusDot');
        const text = document.getElementById('statusText');
        const liveBadge = document.getElementById('liveBadge');

        if (dot) dot.className = `status-dot ${online ? 'online' : 'offline'}`;
        if (text) text.textContent = online ? 'Онлайн · Real-time' : 'Офлайн';
        if (liveBadge) liveBadge.classList.toggle('offline', !online);
    },

    setLastUpdate(serverTime) {
        const el = document.getElementById('lastUpdate');
        if (el) {
            const time = serverTime ? new Date(serverTime) : new Date();
            el.textContent = `Обновлено: ${time.toLocaleTimeString('ru-RU')}`;
        }
    },

    startCountdown(seconds) {
        this.secondsToRefresh = seconds;

        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
        }

        this.updateCountdownDisplay();

        this.countdownTimer = setInterval(() => {
            this.secondsToRefresh -= 1;
            if (this.secondsToRefresh <= 0) {
                this.secondsToRefresh = seconds;
            }
            this.updateCountdownDisplay();
        }, 1000);
    },

    resetCountdown(seconds) {
        this.secondsToRefresh = seconds;
        this.updateCountdownDisplay();
    },

    updateCountdownDisplay() {
        const el = document.getElementById('countdown');
        if (!el) return;

        const min = Math.floor(this.secondsToRefresh / 60);
        const sec = this.secondsToRefresh % 60;
        el.textContent = `След. обновление: ${min}:${sec.toString().padStart(2, '0')}`;
    },

    formatPrice(price, currency = '') {
        if (price === null || price === undefined) return '—';

        const formatted = price >= 1000
            ? price.toLocaleString('ru-RU', { maximumFractionDigits: 2 })
            : price >= 1
                ? price.toLocaleString('ru-RU', { maximumFractionDigits: 4 })
                : price.toLocaleString('ru-RU', { maximumFractionDigits: 8 });

        if (currency === 'USD') return `$${formatted}`;
        if (currency === 'RUB') return `${formatted} ₽`;
        return formatted;
    },

    formatChangeBadge(change) {
        const value = change ?? 0;
        const sign = value > 0 ? '+' : '';
        const cssClass = value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
        const arrow = value > 0 ? '▲' : value < 0 ? '▼' : '—';
        const barWidth = Math.min(Math.abs(value) * 3, 100);

        return `
            <div class="change-cell">
                <span class="change-badge ${cssClass}">${arrow} ${sign}${value}%</span>
                <div class="change-bar-track">
                    <div class="change-bar-fill ${cssClass}" style="width: ${barWidth}%"></div>
                </div>
            </div>
        `;
    },

    formatDateTime(isoDate) {
        if (!isoDate) return '—';
        return new Date(isoDate).toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    },

    createRateCard(item, type) {
        const symbol = type === 'currency' ? item.code : item.symbol;
        const usd = type === 'currency' ? item.rate_usd : item.price_usd;
        const rub = type === 'currency' ? item.rate_rub : item.price_rub;
        const change = item.change_percent_7d ?? 0;
        const changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : '';
        const changeSign = change > 0 ? '+' : '';
        const barWidth = Math.min(Math.abs(change) * 3, 100);

        return `
            <div class="rate-card" data-symbol="${symbol}" data-type="${type}">
                <div class="rate-card-header">
                    <span class="rate-card-symbol">${symbol}</span>
                    <span class="rate-card-type">${type === 'currency' ? 'FIAT' : 'CRYPTO'}</span>
                </div>
                <div class="rate-card-prices">
                    <div class="rate-card-price">${this.formatPrice(usd, 'USD')}</div>
                    <div class="rate-card-price-rub">${this.formatPrice(rub, 'RUB')}</div>
                </div>
                <div class="rate-card-name">${item.name}</div>
                <div class="rate-card-change ${changeClass}">
                    ${changeSign}${change}% за 7 дней
                </div>
                <div class="change-bar-track card-bar">
                    <div class="change-bar-fill ${changeClass}" style="width: ${barWidth}%"></div>
                </div>
            </div>
        `;
    },

    renderCards(containerId, items, type) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!items || items.length === 0) {
            container.innerHTML = '<p class="empty-message">Нет данных</p>';
            return;
        }

        container.innerHTML = items.map(item => this.createRateCard(item, type)).join('');
    },

    renderRatesTable(currencies, cryptos, filter = 'all') {
        const tbody = document.getElementById('ratesTableBody');
        if (!tbody) return;

        let rows = [];

        if (filter === 'all' || filter === 'currencies') {
            currencies.forEach(item => rows.push(this.createTableRow(item, 'currency')));
        }
        if (filter === 'all' || filter === 'crypto') {
            cryptos.forEach(item => rows.push(this.createTableRow(item, 'crypto')));
        }

        // Сортировка: сначала лидеры роста, потом падения
        rows.sort((a, b) => (b._change ?? 0) - (a._change ?? 0));

        if (rows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">Нет данных для отображения</td></tr>';
            return;
        }

        tbody.innerHTML = rows.map(r => r.html).join('');
    },

    createTableRow(item, type) {
        const symbol = type === 'currency' ? item.code : item.symbol;
        const usd = type === 'currency' ? item.rate_usd : item.price_usd;
        const rub = type === 'currency' ? item.rate_rub : item.price_rub;
        const change = item.change_percent_7d ?? 0;

        return {
            _change: change,
            html: `
            <tr data-symbol="${symbol}" data-type="${type}">
                <td><span class="asset-badge">${symbol.substring(0, 3)}</span></td>
                <td>${item.name}</td>
                <td class="price-cell">${this.formatPrice(usd, 'USD')}</td>
                <td class="price-cell">${this.formatPrice(rub, 'RUB')}</td>
                <td>${this.formatChangeBadge(change)}</td>
                <td>${this.formatDateTime(item.updated_at)}</td>
            </tr>
        `,
        };
    },

    renderAllCurrencies(currencies) {
        const tbody = document.getElementById('allCurrenciesBody');
        if (!tbody) return;

        tbody.innerHTML = currencies.map(item => `
            <tr>
                <td><span class="asset-badge">${item.code}</span></td>
                <td>${item.name}</td>
                <td class="price-cell">${this.formatPrice(item.rate_usd, 'USD')}</td>
                <td class="price-cell">${this.formatPrice(item.rate_rub, 'RUB')}</td>
                <td>${this.formatChangeBadge(item.change_percent_7d)}</td>
                <td>${this.formatDateTime(item.updated_at)}</td>
                <td>
                    <button class="btn-favorite ${this.isFavorite(item.code, 'currency') ? 'active' : ''}"
                            data-symbol="${item.code}" data-type="currency" title="В избранное">★</button>
                </td>
            </tr>
        `).join('');
    },

    renderAllCrypto(cryptos) {
        const tbody = document.getElementById('allCryptoBody');
        if (!tbody) return;

        tbody.innerHTML = cryptos.map(item => `
            <tr>
                <td><span class="asset-badge">${item.symbol}</span></td>
                <td>${item.name}</td>
                <td class="price-cell">${this.formatPrice(item.price_usd, 'USD')}</td>
                <td class="price-cell">${this.formatPrice(item.price_rub, 'RUB')}</td>
                <td>${this.formatChangeBadge(item.change_percent_7d)}</td>
                <td>${this.formatDateTime(item.updated_at)}</td>
                <td>
                    <button class="btn-favorite ${this.isFavorite(item.symbol, 'crypto') ? 'active' : ''}"
                            data-symbol="${item.symbol}" data-type="crypto" title="В избранное">★</button>
                </td>
            </tr>
        `).join('');
    },

    renderUpdates(updates) {
        const list = document.getElementById('updatesList');
        if (!list) return;

        if (!updates || updates.length === 0) {
            list.innerHTML = '<li class="loading-item">Нет обновлений</li>';
            return;
        }

        list.innerHTML = updates.map(item => `
            <li>
                <span class="update-symbol">${item.symbol}</span>
                <span class="update-type">${item.asset_type === 'crypto' ? 'CRYPTO' : 'FIAT'}</span>
                <span class="update-price">${this.formatPrice(item.price_usd, 'USD')} / ${this.formatPrice(item.price_rub, 'RUB')}</span>
                <span class="update-time">${this.formatDateTime(item.recorded_at)}</span>
            </li>
        `).join('');
    },

    renderSearchResults(data) {
        const container = document.getElementById('searchResults');
        if (!container) return;

        const currencies = data.currencies || [];
        const cryptos = data.cryptocurrencies || [];

        if (currencies.length === 0 && cryptos.length === 0) {
            container.innerHTML = '<div class="search-result-item"><span>Ничего не найдено</span></div>';
            container.classList.add('visible');
            return;
        }

        let html = '';

        if (currencies.length > 0) {
            html += '<div class="search-result-group"><div class="search-result-group-title">Валюты</div>';
            currencies.forEach(item => {
                html += `
                    <div class="search-result-item" data-symbol="${item.code}" data-type="currency">
                        <div>
                            <div class="search-result-name">${item.name}</div>
                            <div class="search-result-code">${item.code}</div>
                        </div>
                        <div class="search-result-prices">
                            <span class="search-result-price">${this.formatPrice(item.rate_usd, 'USD')}</span>
                            <span class="search-result-price-rub">${this.formatPrice(item.rate_rub, 'RUB')}</span>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }

        if (cryptos.length > 0) {
            html += '<div class="search-result-group"><div class="search-result-group-title">Криптовалюты</div>';
            cryptos.forEach(item => {
                html += `
                    <div class="search-result-item" data-symbol="${item.symbol}" data-type="crypto">
                        <div>
                            <div class="search-result-name">${item.name}</div>
                            <div class="search-result-code">${item.symbol}</div>
                        </div>
                        <div class="search-result-prices">
                            <span class="search-result-price">${this.formatPrice(item.price_usd, 'USD')}</span>
                            <span class="search-result-price-rub">${this.formatPrice(item.price_rub, 'RUB')}</span>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }

        container.innerHTML = html;
        container.classList.add('visible');
    },

    hideSearchResults() {
        const container = document.getElementById('searchResults');
        if (container) container.classList.remove('visible');
    },

    isFavorite(symbol, type) {
        return this.favorites.some(f => f.symbol === symbol && f.type === type);
    },

    toggleFavorite(symbol, type, name) {
        const index = this.favorites.findIndex(f => f.symbol === symbol && f.type === type);

        if (index >= 0) {
            this.favorites.splice(index, 1);
            UI.showToast(`${symbol} удалён из избранного`, 'info');
        } else {
            this.favorites.push({ symbol, type, name });
            UI.showToast(`${symbol} добавлен в избранное`, 'success');
        }

        localStorage.setItem('finrate_favorites', JSON.stringify(this.favorites));
        this.renderFavorites();
    },

    renderFavorites() {
        const container = document.getElementById('favoritesCards');
        if (!container) return;

        if (this.favorites.length === 0) {
            container.innerHTML = '<p class="empty-message">Добавьте активы в избранное, нажав ★ в таблице</p>';
            return;
        }

        container.innerHTML = this.favorites.map(fav => `
            <div class="rate-card">
                <div class="rate-card-header">
                    <span class="rate-card-symbol">${fav.symbol}</span>
                    <span class="rate-card-type">${fav.type === 'currency' ? 'FIAT' : 'CRYPTO'}</span>
                </div>
                <div class="rate-card-name">${fav.name || fav.symbol}</div>
                <button class="btn-favorite active" data-symbol="${fav.symbol}" data-type="${fav.type}">★</button>
            </div>
        `).join('');
    },

    populateChartSymbols(currencies, cryptos, assetType) {
        const select = document.getElementById('chartSymbol');
        if (!select) return;

        const items = assetType === 'currency' ? currencies : cryptos;
        select.innerHTML = items.map(item => {
            const symbol = assetType === 'currency' ? item.code : item.symbol;
            return `<option value="${symbol}">${symbol} — ${item.name}</option>`;
        }).join('');
    },

    showSection(sectionId) {
        document.querySelectorAll('.page-section').forEach(section => {
            section.classList.remove('active');
        });

        const target = document.getElementById(`section-${sectionId}`);
        if (target) target.classList.add('active');

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.section === sectionId);
        });

        document.getElementById('sidebar')?.classList.remove('open');
    },

    flashUpdatedPrices() {
        document.querySelectorAll('.price-cell, .rate-card-price, .rate-card-price-rub').forEach(el => {
            el.classList.add('price-flash');
            setTimeout(() => el.classList.remove('price-flash'), 800);
        });
    },
};
