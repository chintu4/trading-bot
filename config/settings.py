from decouple import config

# General Settings
ENVIRONMENT = config("ENVIRONMENT", default="development")

# CoinDCX API Keys
COINDCX_API_KEY = config("COINDCX_API_KEY")
COINDCX_API_SECRET = config("COINDCX_API_SECRET")

# Binance API Keys
# BINANCE_API_KEY = config("BINANCE_API_KEY")
# BINANCE_API_SECRET = config("BINANCE_API_SECRET")

# Trading Parameters
TRADE_QUANTITY = config("TRADE_QUANTITY", cast=float, default=0.001)
BUY_THRESHOLD = config("BUY_THRESHOLD", cast=float, default=2)  # Buy when price increases by more than 2%
SELL_THRESHOLD = config("SELL_THRESHOLD", cast=float, default=2)  # Sell when price decreases by more than 2%
