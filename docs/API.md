# REST API Documentation

## Base URL

```
http://localhost:5000/api
```

## Endpoints

### GET /api/currencies

Получить список фиатных валют.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| popular | boolean | Только популярные валюты |
| code | string | Получить одну валюту по коду |

**Response:**

```json
{
  "success": true,
  "count": 20,
  "data": [
    {
      "id": 1,
      "name": "US Dollar",
      "code": "USD",
      "rate": 1.0,
      "updated_at": "2026-05-30T12:00:00+00:00"
    }
  ]
}
```

### GET /api/crypto

Получить список криптовалют.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| popular | boolean | Только популярные |
| symbol | string | Получить одну по символу |

### GET /api/search

Поиск по валютам и криптовалютам.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Строка поиска |

**Response:**

```json
{
  "success": true,
  "query": "bit",
  "total": 2,
  "data": {
    "currencies": [],
    "cryptocurrencies": [
      {
        "id": 1,
        "name": "Bitcoin",
        "symbol": "BTC",
        "price": 67500.0,
        "updated_at": "2026-05-30T12:00:00+00:00"
      }
    ]
  }
}
```

### GET /api/history

История изменения курса.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | string | Код валюты или символ крипто |
| type | string | `currency` или `crypto` (default: crypto) |
| days | integer | Количество дней (1-90, default: 7) |
| pair | string | Специальная пара: `btc_rub` |

**Response:**

```json
{
  "success": true,
  "data": {
    "symbol": "BTC",
    "asset_type": "crypto",
    "days": 7,
    "history": [
      {
        "id": 1,
        "asset_type": "crypto",
        "symbol": "BTC",
        "price": 67000.0,
        "recorded_at": "2026-05-23T12:00:00+00:00"
      }
    ],
    "change_percent": 2.5,
    "current_price": 67500.0,
    "first_price": 65800.0
  }
}
```

### GET /api/updates

Последние обновления курсов.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Количество записей (1-50, default: 10) |

## Error Responses

```json
{
  "success": false,
  "error": "Описание ошибки"
}
```

HTTP Status Codes: 400 (Bad Request), 404 (Not Found), 500 (Internal Server Error)
