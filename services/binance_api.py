import requests
from services.exchange_api import ExchangeAPI
from binance.um_futures import UMFutures

import ta
import pandas as pd
# from time import sleep
from binance.error import ClientError
from dotenv import load_dotenv
import os

from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
# dotenv.load(dotenv_path=env_path)
load_dotenv(dotenv_path=env_path)
# api_key = os.getenv("COINDCX_API_KEY")
# api_secret = os.getenv("COINDCX_API_SECRET")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

class BinanceAPI(ExchangeAPI):
    BASE_URL = "https://api.binance.com"

    def __init__(self, api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET):
        self.api_key = api_key
        self.api_secret = api_secret
        
    
# load_env()


    def get_market_data(self):
        endpoint = "/api/v3/exchangeInfo"
        response = requests.get(self.BASE_URL + endpoint)
        return response.json()

    def get_latest_price(self, symbol):
        endpoint = f"/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(self.BASE_URL + endpoint)
        data = response.json()
        return float(data['price'])

    def place_order(self, symbol, quantity, price, order_side, order_type):
        # Binance-specific order logic (simplified)
        pass
    ###################below part is futures

    def get_balance_usdt(self):
        client = UMFutures(key = self.api_key, secret=self.api_secret)

        try:
            response = client.balance(recvWindow=6000)
            for elem in response:
                if elem['asset'] == 'USDT':
                    return float(elem['balance'])

        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

