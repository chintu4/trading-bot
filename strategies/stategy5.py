
import time
import hashlib
import json
import requests
import pandas as pd
import hmac
import hmac
import hashlib
import base64
import json
import time


# Replace with actual API credentials
api_key = "f0953d53d66d2909d0e24e45a692b5066c907d2530d16a7f"  # Replace with your API key
api_secret = "2292ac809896e56bb159a2516d37ec679ac2dccebbc86b0de49fbd2cd749ce95"  # Replace with your API secret
secret_bytes = bytes(api_secret, encoding="utf-8")

SYMBOL = 'B-BTC_USDT'  # Consider renaming to BTC_USDT for clarity
INTERVAL = '15m'
RSI_WINDOW = 14
RSI_BUY_THRESHOLD = 30
RSI_SELL_THRESHOLD = 70
INVESTMENT_AMOUNT = 110
LEVERAGE = 1  # Ensure leverage is supported and used correctly
SLEEP_INTERVAL = 60 * 5

# CoinDCX API Base URLs
CANDLES_URL = 'https://public.coindcx.com/market_data/candles'
TICKER_URL = "https://api.coindcx.com/exchange/ticker"
ORDER_URL = "https://api.coindcx.com/exchange/v1/orders/create"


def check_spot_balance():
    pass

    # Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
    key = api_key
    rsecret = api_secret
    # python3
    secret_bytes = bytes(rsecret, encoding='utf-8')
    # Generating a timestamp
    timeStamp = int(round(time.time() * 1000))
    body = {
    "timestamp": timeStamp
    }
    json_body = json.dumps(body, separators = (',', ':'))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    url = "https://api.coindcx.com/exchange/v1/users/balances"
    headers = {
    'Content-Type': 'application/json',
    'X-AUTH-APIKEY': key,
    'X-AUTH-SIGNATURE': signature
    }
    response = requests.post(url, data = json_body, headers = headers)
    data = response.json()
    cake=pd.DataFrame(data)
    print(cake)


def get_candlestick_data(symbol, interval):
    params = {'pair': symbol, 'interval': interval}
    response = requests.get(CANDLES_URL, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return response.json()


def calculate_rsi(data, window):
    df = pd.DataFrame(data)
    df['close'] = pd.to_numeric(df['close'])  # More robust conversion
    df = df[::-1]  # Reverse for chronological order
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean().abs()  # Ensure loss is positive
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df


def get_spot_ltp():
    response = requests.get(TICKER_URL)
    response.raise_for_status()
    return pd.DataFrame(response.json())


def place_order(side,market,price,total_quantity):
    key = api_key
    secret = api_secret
    # python3
    secret_bytes = bytes(secret, encoding='utf-8')
    # python2
    # secret_bytes = bytes(secret)
    # Generating a timestamp.
    timeStamp = int(round(time.time() * 1000))
    body = {
    "side": side, #Toggle between 'buy' or 'sell'.
    "order_type": "limit_order", #Toggle between a 'market_order' or 'limit_order'.
    "market": market, #Replace 'SNTBTC' with your desired market pair.
    "price_per_unit": price, #This parameter is only required for a 'limit_order'
    "total_quantity": total_quantity, #Replace this with the quantity you want
    "timestamp": timeStamp,
    "client_order_id": "2022.02.14-btcinr_1" #Replace this with the client order id you want
    }
    json_body = json.dumps(body, separators = (',', ':'))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    url = "https://api.coindcx.com/exchange/v1/orders/create"
    headers = {
    'Content-Type': 'application/json',
    'X-AUTH-APIKEY': key,
    'X-AUTH-SIGNATURE': signature
    }
    response = requests.post(url, data = json_body, headers = headers)
    data = response.json()
    print(data)


def calculate_quantity(investment_amount, price):
    return (investment_amount / price)  # Consider using more decimal places if needed


def run_rsi_bot():
    while True:
        try:
            data = get_candlestick_data(SYMBOL, INTERVAL)
            df = calculate_rsi(data, RSI_WINDOW)
            latest_data = df.iloc[-1]
            latest_close = latest_data['close']
            latest_rsi = latest_data['rsi']

            print(f"Current Price: {latest_close}, RSI: {latest_rsi}")  # Monitor values

            if latest_rsi < RSI_BUY_THRESHOLD:
                quantity = calculate_quantity(INVESTMENT_AMOUNT, latest_close)
                order_response = place_order("buy", SYMBOL, latest_close, quantity)
                print(f"Placed Buy Order: {order_response}")
            elif latest_rsi > RSI_SELL_THRESHOLD:
                quantity = calculate_quantity(INVESTMENT_AMOUNT, latest_close)
                order_response = place_order("sell", SYMBOL, latest_close, quantity)
                print(f"Placed Sell Order: {order_response}")

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
        except Exception as e:
            print(f"General Error: {e}")

        time.sleep(SLEEP_INTERVAL)


def arbitrage_opportunity():
    try:
        spot_df = get_spot_ltp()
        btc_inr_price = spot_df[spot_df['market'] == 'BTCINR']['last_price'].iloc[0] #.values[0] is not recommended, .iloc[0] is better
        btc_usdt_price = spot_df[spot_df['market'] == 'BTCUSDT']['last_price'].iloc[0]
        usdt_inr_price = spot_df[spot_df['market'] == 'USDTINR']['last_price'].iloc[0]

        btc_inr = float(btc_inr_price)
        btc_usdt = float(btc_usdt_price)
        usdt_inr = float(usdt_inr_price)
        btc_calculated_value = btc_usdt * usdt_inr

        print(f"BTC/INR: {btc_inr}, BTC/USDT: {btc_usdt}, USDT/INR: {usdt_inr}, Calculated BTC/INR: {btc_calculated_value}")

        if btc_calculated_value > btc_inr:
            print("opportunity to buy")
            
            quantity = float("{:.2f}".format(calculate_quantity(INVESTMENT_AMOUNT, usdt_inr)))  # Buy USDT with INR
            btc_quantity = float("{:.5f}".format(calculate_quantity(INVESTMENT_AMOUNT, btc_usdt)))
            if quantity>0.00001:
                buy_usdt_inr_response = place_order("buy", "USDTINR", usdt_inr, btc_quantity)
                  # Buy BTC with USDT
                buy_btc_usdt_response = place_order("buy", "BTCUSDT", btc_usdt, btc_quantity)
                # quantity = "{:.5f}".format(calculate_quantity(INVESTMENT_AMOUNT, btc_inr)) # Sell BTC for INR
                sell_btc_inr_response = place_order("sell", "BTCINR", btc_inr, quantity)
            else:
                print("quantity less for buy side")
            print(f"Buy USDT/INR: {buy_usdt_inr_response}")
            print(f"Buy BTC/USDT: {buy_btc_usdt_response}")
            print(f"Sell BTC/INR: {sell_btc_inr_response}")

        elif btc_calculated_value < btc_inr:
            print("opportunity to sell")
            # quantity = calculate_quantity(INVESTMENT_AMOUNT, btc_inr)  # Buy BTC with INR
            # quantity = float("{:.5f}".format(calculate_quantity(INVESTMENT_AMOUNT, btc_inr)))
            # quantity=float(f"{calculate_quantity(INVESTMENT_AMOUNT, btc_inr):.5f}")
            quantity=0.00001
            
            print(quantity)
            if quantity>=0.00001:
                buy_btc_inr_response = place_order("buy", "BTCINR", btc_inr, quantity)
                sell_btc_usdt_response = place_order("sell", "BTCUSDT", btc_usdt, quantity)
                quantity = float("{:.2f}".format(calculate_quantity(INVESTMENT_AMOUNT, usdt_inr) ) )# Sell USDT for INR
                sell_usdt_inr_response = place_order("sell", "USDTINR", usdt_inr, quantity)
                
            else:
                print("quantity is less than for")
            # quantity = "{:.5f}".format(calculate_quantity(INVESTMENT_AMOUNT, btc_usdt))  # Sell BTC for USDT
            

            print(f"Buy BTC/INR: {buy_btc_inr_response}")
            print(f"Sell BTC/USDT: {sell_btc_usdt_response}")
            print(f"Sell USDT/INR: {sell_usdt_inr_response}")
        else:
            print("No arbitrage opportunity")

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
    except IndexError as e:
      print(f"Index Error: {e}, likely market data is missing for one of the pairs")
    
def main():
    # check_spot_balance()
    arbitrage_opportunity()
main()