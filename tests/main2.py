import requests
import json
import os
from dotenv import load_dotenv
from services.exchange_api import ExchangeAPI
from services.coindcx_api import CoinDCXAPI
from services.binance_api import BinanceAPI
import json
import pandas as pd
import ccxt as cx

binance=BinanceAPI()
print(binance.get_balance_usdt())

