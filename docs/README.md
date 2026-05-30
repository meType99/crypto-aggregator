# FinRate — Агрегатор курсов валют и криптовалют

Полноценный веб-проект для мониторинга актуальных курсов фиатных валют и криптовалют.

## Технологии

| Компонент | Технология |
|-----------|-----------|
| Backend | Python + Flask |
| Frontend | HTML, CSS, JavaScript |
| База данных | SQLite |
| Графики | Chart.js |
| API | REST (JSON) |

## Структура проекта

```
project/
├── backend/
│   ├── app.py              # Точка входа Flask
│   ├── config.py           # Конфигурация
│   ├── routes/             # REST API маршруты
│   ├── services/           # Бизнес-логика
│   ├── models/             # SQLAlchemy модели
│   ├── database/           # Подключение к БД
│   └── utils/              # Логирование
├── frontend/
│   ├── index.html          # Главная страница
│   ├── css/                # Стили
│   └── js/                 # JavaScript модули
├── data/                   # Файл SQLite (создаётся автоматически)
├── docs/                   # Документация
├── requirements.txt
└── run.py                  # Скрипт запуска
```

## Быстрый старт

### 1. Python-окружение

```bash
cd project
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Конфигурация (опционально)

```bash
copy .env.example .env
```

PostgreSQL не нужен. База SQLite создаётся автоматически в `data/currency_aggregator.db`.

### 3. Запуск

```bash
python run.py
```

Откройте http://localhost:5000

## Поделиться ссылкой с другими

Чтобы **любой человек** мог открыть сайт по ссылке, см. **[docs/SHARE.md](SHARE.md)**:

- **ngrok** — быстро, пока ваш ПК включён (5 минут)
- **Render.com** — постоянная ссылка 24/7 (через GitHub)

## REST API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/currencies` | Список валют |
| GET | `/api/currencies?popular=true` | Популярные валюты |
| GET | `/api/crypto` | Список криптовалют |
| GET | `/api/crypto?popular=true` | Популярные криптовалюты |
| GET | `/api/search?q=BTC` | Поиск |
| GET | `/api/history?symbol=BTC&type=crypto&days=7` | История курса |
| GET | `/api/history?pair=btc_rub&days=7` | График BTC/RUB |
| GET | `/api/updates?limit=10` | Последние обновления |

## Внешние API

- **Валюты:** [open.er-api.com](https://open.er-api.com) (бесплатный, без ключа)
- **Криптовалюты:** [CoinGecko API](https://www.coingecko.com/en/api) (бесплатный)

## Автообновление

Backend автоматически обновляет данные каждые 5 минут (настраивается через `UPDATE_INTERVAL`).
