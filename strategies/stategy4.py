import time
import hashlib
import json
import requests
import pandas as pd
import hmac


# Replace with actual API credentials
api_key="f0953d53d66d2909d0e24e45a692b5066c907d2530d16a7f"
api_secret="2292ac809896e56bb159a2516d37ec679ac2dccebbc86b0de49fbd2cd749ce95"
secret_bytes = bytes(api_secret, encoding="utf-8")

SYMBOL = 'B-BTC_USDT'
INTERVAL = '15m'
RSI_WINDOW = 14
RSI_BUY_THRESHOLD = 30
RSI_SELL_THRESHOLD = 70
INVESTMENT_AMOUNT = 50
LEVERAGE = 1
SLEEP_INTERVAL = 60 * 5

def get_candlestick_data(symbol, interval):
    url = f'https://public.coindcx.com/market_data/candles?pair={symbol}&interval={interval}'
    response = requests.get(url)
    return response.json()

def calculate_rsi(data, window):
    df = pd.DataFrame(data)
    df['close'] = df['close'].astype(float)
    df = df[::-1]
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df
def get_spot_ltp():
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)
    return pd.DataFrame(response.json())

def place_order(side, symbol, limit_price, quantity):
    timestamp = int(time.time() * 1000)
    body = {
        "timestamp": timestamp,
        "market": symbol,
        "side": side,
        "order_type": "limit_order",
        "limit_price": limit_price,
        "quantity": quantity,
        "leverage": LEVERAGE,
    }
    json_body = json.dumps(body, separators=(',', ':'))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    url = "https://api.coindcx.com/exchange/v1/orders/create"
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": api_key,
        "X-AUTH-SIGNATURE": signature
    }
    response = requests.post(url, data=json_body, headers=headers)
    return response.json()

def calculate_quantity(investment_amount, price):
    return round(investment_amount / price, 6)

def run_rsi_bot():
    while True:
        try:
            data = get_candlestick_data(SYMBOL, INTERVAL)
            df = calculate_rsi(data, RSI_WINDOW)
            latest_data = df.iloc[-1]
            latest_close = latest_data['close']
            latest_rsi = latest_data['rsi']
            
            if latest_rsi < RSI_BUY_THRESHOLD:
                quantity = calculate_quantity(INVESTMENT_AMOUNT, latest_close)
                order_response = place_order("buy", SYMBOL, latest_close, quantity)
                print(f"Placed Buy Order: {order_response}")
            elif latest_rsi > RSI_SELL_THRESHOLD:
                quantity = calculate_quantity(INVESTMENT_AMOUNT, latest_close)
                order_response = place_order("sell", SYMBOL, latest_close, quantity)
                print(f"Placed Sell Order: {order_response}")
        except Exception as e:
            print(f"Error occurred: {e}")
        time.sleep(SLEEP_INTERVAL)

def arbitrage_opportunity():
    spot_df = get_spot_ltp()
    btc_inr = float(spot_df[spot_df['market'] == 'BTCINR']['last_price'].values[0])
    btc_usdt = float(spot_df[spot_df['market'] == 'BTCUSDT']['last_price'].values[0])
    usdt_inr = float(spot_df[spot_df['market'] == 'USDTINR']['last_price'].values[0])
    btc_calculated_value = btc_usdt * usdt_inr

    print(f"BTC/INR: {btc_inr}, BTC/USDT: {btc_usdt}, USDT/INR: {usdt_inr}, Calculated BTC/INR: {btc_calculated_value}")
    
    if btc_calculated_value < btc_inr:
        quantity = calculate_quantity(INVESTMENT_AMOUNT, btc_inr)
        buy_response = place_order("buy", "BTCINR", btc_inr, quantity)
        print(f"Buy BTC/INR Order Response: {buy_response}")
    elif btc_calculated_value > btc_inr:
        quantity = calculate_quantity(INVESTMENT_AMOUNT, btc_usdt)
        
        buy_response = place_order("buy", "BTCUSDT", btc_usdt, quantity)
        sell_response = place_order("sell", "BTCINR", btc_inr, quantity)
        print(f"Buy BTC/USDT Order Response: {buy_response}")
        print(f"Sell BTC/INR Order Response: {sell_response}")
    else:
        print("No arbitrage opportunity")

def run_arbitrage_bot():
    while True:
        try:
            arbitrage_opportunity()
        except Exception as e:
            print(f"Error occurred: {e}")
        time.sleep(SLEEP_INTERVAL)
