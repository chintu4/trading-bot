import hmac
import hashlib
import base64
import json
import time
import requests

api_key = "f0953d53d66d2909d0e24e45a692b5066c907d2530d16a7f"  # Replace with your API key
api_secret = "2292ac809896e56bb159a2516d37ec679ac2dccebbc86b0de49fbd2cd749ce95" 
# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
def place_order(side,market,price,total_quantity):
    api_key = "f0953d53d66d2909d0e24e45a692b5066c907d2530d16a7f"  # Replace with your API key
    api_secret = "2292ac809896e56bb159a2516d37ec679ac2dccebbc86b0de49fbd2cd749ce95" 
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
    "order_type": "market_order", #Toggle between a 'market_order' or 'limit_order'.
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


# buy_btc_inr_response = place_order("buy", "BTCINR", btc_inr, quantity)
sell_btc_usdt_response = place_order("buy", "BTCINR",96608.0, 0.00002)
# quantity = float("{:.2f}".format(calculate_quantity(INVESTMENT_AMOUNT, usdt_inr) ) )# Sell USDT for INR
# sell_usdt_inr_response = place_order("sell", "USDTINR", usdt_inr, quantity)