import os
import json
import hmac
import hashlib
import time
import asyncio
import requests
import socketio
import sys
import pandas as pd
import ta  # Technical analysis indicators
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from coindcx_api import CoinDCXAPI

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("COINDCX_API_KEY")
API_SECRET = os.getenv("COINDCX_API_SECRET")
socketEndpoint = 'wss://stream.coindcx.com'

# User-defined trading pair (INR Futures)
INSTRUMENT = input("Enter INR Futures trading pair (e.g., BTC_INR_FUT, ETH_INR_FUT): ").strip().upper()
QUOTE_CURRENCY = "INR"
BASE_CURRENCY = INSTRUMENT.split("_")[0]  # Extract BTC from BTC_INR_FUT

# Trading parameters
STOP_LOSS_PERCENTAGE = 1.5
PROFIT_TARGET_PERCENTAGE = 3
RISK_PERCENTAGE = 5  # Risk 5% of INR futures balance per trade

# WebSocket Client
sio = socketio.AsyncClient()

# Generate API Signature
def generate_signature(body):
    secret_bytes = bytes(API_SECRET, encoding='utf-8')
    json_body = json.dumps(body, separators=(',', ':'))
    return hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

# Function to fetch futures balance
def get_futures_balance():
    """Fetches INR Futures balance"""
    print(f"[{datetime.now()}] [INFO] Fetching INR Futures balance...")

    endpoint = "https://api.coindcx.com/exchange/v1/futures/balances"
    headers = {"X-AUTH-APIKEY": API_KEY}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        balances = response.json()
        for asset in balances:
            if asset["currency"] == QUOTE_CURRENCY and asset["product"] == "futures":
                return float(asset["balance"])
    
    print(f"[{datetime.now()}] [ERROR] Failed to retrieve INR Futures balance.")
    return 0

# Function to fetch open orders
def get_open_orders():
    """Fetches all open orders for the instrument"""
    print(f"[{datetime.now()}] [INFO] Fetching open orders...")

    endpoint = "https://api.coindcx.com/exchange/v1/orders/open"
    headers = {"X-AUTH-APIKEY": API_KEY}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        orders = [order for order in response.json() if order["market"] == INSTRUMENT]
        return orders

    print(f"[{datetime.now()}] [ERROR] Failed to fetch open orders.")
    return []

# Function to calculate trade quantity
def calculate_trade_quantity(price):
    """Determines how much to buy/sell based on INR futures balance"""
    inr_balance = get_futures_balance()
    trade_amount = (RISK_PERCENTAGE / 100) * inr_balance  # Risk 5% of INR futures balance
    quantity = trade_amount / price  # Convert INR to asset quantity
    return round(quantity, 6)

# Function to place orders
def place_order(side, price):
    """Places a buy or sell order on CoinDCX Futures"""
    print(f"[{datetime.now()}] [INFO] Attempting to place {side.upper()} order at {price}...")

    quantity = calculate_trade_quantity(price)
    if quantity <= 0:
        print(f"[{datetime.now()}] [ERROR] Insufficient INR balance to place order.")
        return

    order_data = {
        "market": INSTRUMENT,
        "side": side,  # "buy" or "sell"
        "order_type": "limit_order",
        "price": price,
        "quantity": quantity,
        "timestamp": int(time.time() * 1000)
    }
    signature = generate_signature(order_data)

    headers = {
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature,
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.coindcx.com/exchange/v1/futures/orders/create", headers=headers, json=order_data)
    
    print(f"[{datetime.now()}] [ORDER RESPONSE] {response.json()}")

# WebSocket Events
@sio.event
async def connect():
    print(f"[{datetime.now()}] [CONNECTED] WebSocket Connection Established")
    await sio.emit('join', {'channelName': f"{INSTRUMENT}@prices-futures"})

@sio.event
async def disconnect():
    print(f"[{datetime.now()}] [DISCONNECTED] WebSocket Disconnected. Reconnecting...")
    await asyncio.sleep(5)
    await reconnect()

async def reconnect():
    try:
        print(f"[{datetime.now()}] [RECONNECTING] Attempting WebSocket Reconnection...")
        await sio.connect(socketEndpoint, transports='websocket')
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] WebSocket Reconnection Failed: {e}")
        await asyncio.sleep(10)

# Store recent price data for indicators
price_data = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

@sio.on('candlestick')
async def on_candlestick(response):
    """Handles candlestick data for trading logic"""
    global price_data

    try:
        data = response["data"]
        timestamp = datetime.fromtimestamp(data["timestamp"] / 1000)
        open_price = float(data["open"])
        high = float(data["high"])
        low = float(data["low"])
        close_price = float(data["close"])
        volume = float(data["volume"])

        # Append new candle to price_data
        new_candle = pd.DataFrame([[timestamp, open_price, high, low, close_price, volume]],
                                  columns=price_data.columns)
        price_data = pd.concat([price_data, new_candle], ignore_index=True)

        # Keep only last 50 candles
        if len(price_data) > 50:
            price_data = price_data.iloc[-50:]

        # Compute indicators
        price_data["rsi"] = ta.momentum.RSIIndicator(price_data["close"], window=14).rsi()
        price_data["ema"] = ta.trend.EMAIndicator(price_data["close"], window=9).ema_indicator()

        latest_rsi = price_data["rsi"].iloc[-1]
        latest_ema = price_data["ema"].iloc[-1]

        print(f"[{datetime.now()}] RSI: {latest_rsi:.2f}, EMA: {latest_ema:.2f}")

        # Trading logic
        if latest_rsi < 30 and close_price > latest_ema:
            print(f"[{datetime.now()}] [TRADE] Buying at: {close_price}")
            place_order("buy", close_price)

        elif latest_rsi > 70 and close_price < latest_ema:
            print(f"[{datetime.now()}] [TRADE] Selling at: {close_price}")
            place_order("sell", close_price)

    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Candlestick Processing Failed: {e}")

# Regular updates
async def print_updates():
    """Provides regular updates on balance, open orders, and trading status"""
    while True:
        cdcx=CoinDCXAPI()
        inr_balance = cdcx.get_futures_wallets()
        open_orders = cdcx.get_open_futures_orders()

        print("\n===[Account Update]=====")
        print(f"💰 INR Futures Balance: {inr_balance:.2f}")
        print(f"📋 Open Orders: {len(open_orders)}")
        for order in open_orders:
            print(f"   ↳ {order['side'].upper()} {order['quantity']} at {order['price']} (Status: {order['status']})")

        print("========================\n")
        await asyncio.sleep(30)  # Update every 30 seconds

# Keep connection alive
async def main():
    await asyncio.gather(
        sio.connect(socketEndpoint, transports='websocket'),
        print_updates(),
        sio.wait()
    )


# Run the script
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
