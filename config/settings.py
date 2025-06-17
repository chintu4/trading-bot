import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Cosmos DB Configuration
COSMOS_DB_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT")
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")

# Example of how to use:
# if not COSMOS_DB_ENDPOINT or not COSMOS_DB_KEY:
#     print("ERROR: COSMOS_DB_ENDPOINT and COSMOS_DB_KEY must be set in your .env file.")
# else:
#     print(f"Cosmos DB Endpoint: {COSMOS_DB_ENDPOINT}")
#     # Key is sensitive, avoid printing it directly in production logs
#     print(f"Cosmos DB Key is set (length: {len(COSMOS_DB_KEY) if COSMOS_DB_KEY else 0})")

# Add other configurations below as needed
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") # Assuming you might have this
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")   # Assuming you might have this

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
