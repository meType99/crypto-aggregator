"""
Общие константы сервисного слоя.
"""

# CoinGecko id -> (symbol, name)
TRACKED_CRYPTO = {
    'bitcoin': ('BTC', 'Bitcoin'),
    'ethereum': ('ETH', 'Ethereum'),
    'tether': ('USDT', 'Tether'),
    'binancecoin': ('BNB', 'Binance Coin'),
    'solana': ('SOL', 'Solana'),
    'ripple': ('XRP', 'Ripple'),
    'cardano': ('ADA', 'Cardano'),
    'dogecoin': ('DOGE', 'Dogecoin'),
    'tron': ('TRX', 'TRON'),
    'polkadot': ('DOT', 'Polkadot'),
    'litecoin': ('LTC', 'Litecoin'),
    'chainlink': ('LINK', 'Chainlink'),
}

SYMBOL_TO_COINGECKO = {
    info[0]: coin_id for coin_id, info in TRACKED_CRYPTO.items()
}
