import hmac
import hashlib
import base64
import json
import time
import requests
from dotenv import load_dotenv
from pathlib import Path
import os
from coindcx_api import CoinDCXAPI


env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

key = os.getenv("COINDCX_API_KEY")
secret = os.getenv("COINDCX_API_SECRET")

# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.



# python3
secret_bytes = bytes(secret, encoding='utf-8')
# python2
# secret_bytes = bytes(secret)

# Generating a timestamp
timeStamp = int(round(time.time() * 1000))

body = {
        "timestamp":timeStamp , # EPOCH timestamp in seconds
        "order": {
        "side": "sell", # buy OR sell
        "pair": "B-XRP_USDT", # instrument.string
        "order_type": "market_order", # market_order OR limit_order 
        "price": "2.1855", #numeric value
    "stop_price": "2.1500", #numeric value
        "total_quantity": 6, #numerice value
        "leverage": 100, #numerice value
        "notification": "email_notification", # no_notification OR email_notification OR push_notification
        "time_in_force": "good_till_cancel", # good_till_cancel OR fill_or_kill OR immediate_or_cancel
        "hidden": False, # True or False
        "post_only": False, # True or False,
        "margin_currency_short_name":"INR"
        }
        }

json_body = json.dumps(body, separators = (',', ':'))

signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

url = "https://api.coindcx.com/exchange/v1/derivatives/futures/orders/create"

headers = {
    'Content-Type': 'application/json',
    'X-AUTH-APIKEY': key,
    'X-AUTH-SIGNATURE': signature
}

response = requests.post(url, data = json_body, headers = headers)
data = response.json()
print(data)