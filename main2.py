import requests
import json
import os
from dotenv import load_dotenv
from services.exchange_api import ExchangeAPI
from services.coindcx_api import CoinDCXAPI
import json
import pandas as pd


# Load JSON data from a file or API response
# with open('data.json', 'r') as f:
#     data = json.load(f)

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Print the DataFrame
# print(df)
# look i wanted coinprice first
# 2. I wanted iwanted click to sell the coin and the percentage of coin to be saled 
# 3. I wanted quick count,current price.
# 4. 

import requests

def get_current_price(pair):
    url = f"https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)
    data = response.json()
    
    for item in data:
        if item['market'] == pair:
            return item['last_price']
    return None

# Example usage
pair = "SOLINR"  # Replace with your desired market pair
price = get_current_price(pair)
if price:
    print(f"The current price of {pair} is {price}")
else:
    print(f"Price for {pair} not found")




# from model.model import MarketData


load_dotenv()
api_key = os.getenv("COINDCX_API_KEY")
api_secret = os.getenv("COINDCX_API_SECRET")


# # Replace with your CoinDCX API key and secret
# api_key = "YOUR_API_KEY"
# api_secret = "YOUR_API_SECRET"

# Base URL for CoinDCX API
base_url = "https://api.coindcx.com"
base_url2="https://public.coindcx.com"


# def get_bitcoin_current_price():
# url = f"{base_url}/exchange/ticker"
#     "symbol": "BTCUSDT"
# }


# response = requests.get(url, params=params)
# data = response.json()
# print(data)
# with open('data.json', 'w') as json_file:
#     json.dump(data, json_file)
# for item in data:
#     market_data = MarketData(item)
#     # print(market_data.to_json())
# market_data = MarketData.search("PORTOUSDT")
# print(market_data.to_json())

# return float(data["tick"]["close"])

def get_current_price(pair):
    # ... (same as the previous code)
    pass

def place_order(pair, side, order_type, quantity, price):
    # ... (construct the API request and send it to CoinDCX)
    pass

# # Simple trading strategy
# buy_threshold = 10000
# sell_threshold = 12000

# while True:
#     current_price = get_current_price("BTCUSDT")

#     if current_price < buy_threshold:
#         place_order("BTCUSDT", "buy", "limit", 1, buy_threshold)
#     elif current_price > sell_threshold:
#         place_order("BTCUSDT", "sell", "limit", 1, sell_threshold)

#     # Add a delay to avoid excessive API calls
#     time.sleep(60)

# print(get_bitcoin_current_price())

# market,volume,bind,ask,change_24_

# print(get_current_price("BTCUSDT"))

# {'market': 'PORTOUSDT', 'change_24_hour': '2.267', 'high': '2.53900000', 'low': '2.05800000', 'volume': '8134554.33496000', 'last_price': '2.16500000', 'bid': '2.16300000', 'ask': '2.16500000', 'timestamp': 1733663136}, 
# class=CoinDCXAPI ()


# print(CoinDCXAPI(api_key, api_secret).get_latest_price('BTCUSDT'))

# coindcx_api = CoinDCXAPI(api_key, api_secret)
# latest_price = coindcx_api.get_latest_price('BTCUSDT')
# print(f"The latest price for BTCUSDT is: {latest_price}")


# print(MarketData.get_market_data('PORTOUSDT'))

    # with open('data.json', 'w') as outfile:
    #     json.dump(data, outfile)

# import json

# with open('data.json', 'r') as file:
#     data = json.load(file)

# # Example usage: print the loaded data
# print(data)
# market_data = MarketData.search("BTCUSDT")
# print(f"The latest price for BTCUSDT is: {market_data.last_price}")


# market_data = MarketData.search("BTCUSDT")
# print(market_data.to_json())
