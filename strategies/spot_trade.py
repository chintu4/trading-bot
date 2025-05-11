import time
import requests
import hmac
import hashlib
import pandas as pd
from datetime import datetime

# === CONFIGURATION ===
API_KEY = "f0953d53d66d2909d0e24e45a692b5066c907d2530d16a7f"  # Replace with your API key
API_SECRET = "2292ac809896e56bb159a2516d37ec679ac2dccebbc86b0de49fbd2cd749ce95" 
# API_KEY = "your_api_key_here"
# API_SECRET = "your_api_secret_here"
BASE_URL = "https://api.coindcx.com"
TRADE_PAIR = "BTCINR"
FIXED_INVESTMENT = 1000  # INR investment per trade
CSV_FILE = "market_data.csv"
RSI_PERIOD = 14  # RSI lookback period
SMA_PERIOD = 50  # SMA lookback period
PROFIT_TARGET = 1.05  # 5% target profit
STOP_LOSS = 0.98  # 2% stop loss
RISK_PER_TRADE = 0.02  # 2% of total capital per trade

# === API AUTHENTICATION ===
def generate_signature(payload, secret):
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

# === FETCH MARKET DATA ===
def get_latest_price(pair):
    response = requests.get(f"{BASE_URL}/exchange/ticker")
    prices = response.json()
    for market in prices:
        if market["market"] == pair:
            return float(market["ask"]), float(market["bid"])
    return None, None

# === SAVE DATA TO CSV ===
def save_to_csv(data):
    df = pd.DataFrame(data, columns=["timestamp", "ask_price", "bid_price"])
    df.to_csv(CSV_FILE, mode='a', index=False, header=not pd.io.common.file_exists(CSV_FILE))

# === CALCULATE INDICATORS ===
def calculate_indicators(df):
    df["ask_price"] = df["ask_price"].astype(float)
    
    # Calculate SMA
    df["sma"] = df["ask_price"].rolling(window=SMA_PERIOD).mean()
    
    # Calculate RSI
    delta = df["ask_price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    
    return df

# === CHECK TREND AND RSI ===
def check_trend_and_rsi(df):
    if len(df) < SMA_PERIOD:
        return False  # Not enough data to analyze trends
    
    # Check if price is above SMA (uptrend)
    is_uptrend = df["ask_price"].iloc[-1] > df["sma"].iloc[-1]
    
    # Check RSI for overbought/oversold conditions
    rsi = df["rsi"].iloc[-1]
    is_overbought = rsi > 70
    is_oversold = rsi < 30
    
    return is_uptrend, is_overbought, is_oversold

# === PLACE MARKET ORDER ===
def place_order(side, quantity, price):
    endpoint = "/exchange/v1/orders/create"
    payload = {
        "side": side,
        "order_type": "market_order",
        "market": TRADE_PAIR,
        "price_per_unit": price,
        "total_quantity": quantity
    }
    
    payload_str = str(payload).replace("'", '"')
    signature = generate_signature(payload_str, API_SECRET)

    headers = {
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature,
        "Content-Type": "application/json"
    }

    response = requests.post(BASE_URL + endpoint, json=payload, headers=headers)
    return response.json()

# === MAIN TRADING BOT ===
def trading_bot():
    market_data = []

    while True:
        ask_price, bid_price = get_latest_price(TRADE_PAIR)

        if ask_price and bid_price:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            market_data.append([timestamp, ask_price, bid_price])
            save_to_csv(market_data)  # Save every update

            df = pd.read_csv(CSV_FILE)
            df = calculate_indicators(df)
            is_uptrend, is_overbought, is_oversold = check_trend_and_rsi(df)

            # Enter trade only in uptrend and not overbought
            if is_uptrend and not is_overbought:
                quantity = (FIXED_INVESTMENT * RISK_PER_TRADE) / ask_price
                print(f"BUY order: {quantity} BTC at ₹{ask_price}")
                buy_response = place_order("buy", quantity, ask_price)

                if buy_response.get("status") == "success":
                    buy_price = ask_price
                    target_price = buy_price * PROFIT_TARGET
                    stop_loss_price = buy_price * STOP_LOSS
                    print(f"Bought at {buy_price}. Target: {target_price}, Stop Loss: {stop_loss_price}")

                    # Wait until the price hits target profit or stop-loss
                    while True:
                        _, bid_price = get_latest_price(TRADE_PAIR)
                        if bid_price >= target_price:
                            print(f"SELL order at ₹{bid_price} (Profit)")
                            place_order("sell", quantity, bid_price)
                            break
                        elif bid_price <= stop_loss_price:
                            print(f"SELL order at ₹{bid_price} (Stop Loss)")
                            place_order("sell", quantity, bid_price)
                            break
                        time.sleep(5)  # Check price every 5 seconds

        time.sleep(10)  # Fetch market data every 10 seconds

# === RUN THE BOT ===
trading_bot()