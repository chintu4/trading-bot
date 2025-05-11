import requests
import logging
import hmac
import hashlib
import time
import json
import os
import pandas as pd
from ta import add_all_ta_features
from datetime import datetime
from dotenv import load_dotenv
import helper as hp
import plotly.graph_objects as go
import numpy as np
# from services.exchange_api import ExchangeAPI

from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
# dotenv.load(dotenv_path=env_path)
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("COINDCX_API_KEY")
api_secret = os.getenv("COINDCX_API_SECRET")


#TODO ERROR PS C:\Users\dsjapnc\Documents\chintu Sharma\trading Pratform> python main2.py
# ERROR:root:Error during API request: 404 Client Error: Not Found for url: https://api.coindcx.com/exchange/v1/market_details?symbol=BTCUSDT
# The latest price for BTCUSDT is: None


class CoinDCXAPI():

    BASE_URL = "https://api.coindcx.com"
    FUTURE_URL=""

    def __init__(self, api_key=api_key, api_secret=api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.message_toggle=True
        self.secret_bytes = bytes(self.api_secret, encoding='utf-8')
        self.atr_multiplier = 1.5
    def _generate_signature(self,json_body):
        # response = requests.post(url, data = json_body, headers = headers)
        # data = response.json()
        # print(data)
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        return hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        


    
    def ltp(self):
# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.

# python3
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        # python2
        # secret_bytes = bytes(secret)
        # Generating a timestamp
        timeStamp = int(round(time.time() * 1000))
        body = {
        "timestamp":timeStamp , # EPOCH timestamp in seconds
        "page": "1", #no. of pages needed
        "size": "10",
        "margin_currency_short_name": ["INR"]
        }
        json_body = json.dumps(body, separators = (',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/positions"
        headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': self.api_key,
        'X-AUTH-SIGNATURE': signature
        }
        response = requests.post(url, data = json_body, headers = headers)
        data = response.json()
        print(data)
        return data[0]
        # print(data)
    def time_now(self):
        now = datetime.now()
        # Convert to an array format [year, month, day, hour, minute, second]
        time_array = [now.year, now.month, now.day, now.hour, now.minute, now.second]
        return time_array
    # import requests # Install requests module first.
    def get_market_details(self):
        url = "https://api.coindcx.com/exchange/v1/markets_details"
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data)
        # return pd
        # print(data)

    def get_market_data(self):
        url = f"{self.BASE_URL}/exchange/ticker"
        response = requests.get(url,timeout=10)
        data = response.json()
        return data
    
    def get_current_price(self, symbol):
        try :
            data=self.get_market_data()
            for item in data:
                if item['market'] == symbol:
                    return item['last_price']
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current price for {symbol}: {e}")
    

    def place_spot_order_now(self, symbol, quantity, price, order_side, order_type):
        endpoint = "/exchange/v1/orders/create"
        url = self.BASE_URL + endpoint

        timestamp = int(time.time() * 1000)
        payload = {
            "market": symbol,
            "total_quantity": quantity,
            "price_per_unit": price,
            "side": order_side,
            "order_type": order_type,
            "timestamp": timestamp
        }
        json_payload = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(json_payload)

        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": signature
        }

        try:
            # response = requests.post(url, data=json_payload, headers=headers)
            # response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
            # return response.json()
            response = requests.post(url, data=json_payload, headers=headers,timeout=10) 
            response.raise_for_status() # Check for HTTP errors (4xx or 5xx) 
            order_data = response.json() 
            return order_data.get("id") # Retrieve the order ID from the response 
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            print("Response content:", response.content)  # Log the full response content
            return None



    def get_spot_order_status(self, order_id):
        endpoint = "/exchange/v1/orders/status"
        url = self.BASE_URL + endpoint

        timestamp = int(time.time() * 1000)
        payload = {
            "timestamp": timestamp,
            "id": order_id
        }
        json_payload = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(json_payload)

        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": signature
        }

        try:
            response = requests.post(url, data=json_payload, headers=headers,timeout=10)
            response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None

#         return None
    
    def get_percentage_change(self, symbol):
        url = f"{self.BASE_URL}/exchange/ticker"
        response = requests.get(url,timeout=10)
        data = response.json()
        
        for item in data:
            if item['market'] == symbol:
                current_price = float(item['last_price'])
                change_24_hour = float(item['change_24_hour'])
                previous_price = current_price / (1 + change_24_hour / 100)
                percentage_change = ((current_price - previous_price) / previous_price) * 100
                return percentage_change
        return None



    def calculate_total_cost_after_selling(self,quantity, price_per_unit, platform_fee_percentage=0.2, gst_percentage=18):

        # Calculate the total amount before fees
        total_amount = quantity * price_per_unit

        # Calculate the platform fee
        platform_fee = total_amount * (platform_fee_percentage / 100)

        # Calculate the GST on the platform fee
        gst = platform_fee * (gst_percentage / 100)

        # Calculate the total cost after deducting fees and GST
        total_cost_after_selling = total_amount - (platform_fee + gst)

        # Check if the total cost after selling is less than 105 rupees
        if total_cost_after_selling < 105:
            return "Order amount is too low to execute."

        return total_cost_after_selling

    def get_wallet_balance(self,symbol="INR"):
        endpoint = "/exchange/v1/users/balances"
        url = self.BASE_URL + endpoint

        timestamp = int(time.time() * 1000)
        payload = {
            "timestamp": timestamp
        }
        json_payload = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(json_payload)

        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": signature
        }

        try:
            response = requests.post(url, data=json_payload, headers=headers)
            response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
            balances = response.json()
            # return pd.DataFrame(balances)
            
            for balance in balances:
                if balance['currency'] == symbol[:3]:
                    
                    # if balance['locked_balance']:
                    #     return f"Locked {balance['currency']} at {balance['locked_price']}"
                    # else:
                    return float(balance['balance'])
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None

    def get_history_data(self, symbol, start_time, end_time, interval):
        """Retrieve history data for backtesting"""
        endpoint = "/exchange/v1/markets/{symbol}/candles".format(symbol=symbol)
        url = self.BASE_URL + endpoint

        payload = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval
        }
        try:
            response = requests.get(url, params=payload,timeout=10)
            response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None

    def calculate_percentage_change(self, old_price, new_price):
        old_price=float(old_price)
        if (old_price!=new_price):
            return ((new_price - old_price) / old_price) * 100
        else:
            print("old and new price is same")
            return 0
########################################################################################################
######################################################################################################
##################################Futures##################################################
    

    def set_futures_margin_type(self, pair, margin_type):
        """
        Set margin type for a futures position

        :param pair: str, pair for which to set the margin type
        :param margin_type: str, "isolated" or "crossed"
        :return: dict, JSON response from the API containing the result
        """
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        timeStamp = int(round(time.time() * 1000))
        body = {
            "timestamp": timeStamp,
            "pair": pair,
            "margin_type": margin_type
        }
        json_body = json.dumps(body, separators=(',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/positions/margin_type"
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        response = requests.post(url, data=json_body, headers=headers)
        data = response.json()
        return data
    
    def get_conversions(self):
        """
        Get currency conversion 
        Get the conversion rates for all currency pairs

        :return: dict, JSON response from the API containing the conversion rates
        """
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        timeStamp = int(round(time.time() * 1000))
        body = {
            "timestamp": timeStamp,
        }
        json_body = json.dumps(body, separators=(',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/api/v1/derivatives/futures/data/conversions"
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        response = requests.get(url, data=json_body, headers=headers)
        data = response.json()
        return data
    


    def get_min_max_quantity(self, pair):
        """
        Get min and max quantity of a futures pair

        :param pair: str, pair for which to get the min and max quantity
        :return: dict, JSON response from the API containing the min and max quantity
        """
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        timeStamp = int(round(time.time() * 1000))
        body = {
            "timestamp": timeStamp,
            "pair": pair
        }
        json_body = json.dumps(body, separators=(',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/position/limits"
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        response = requests.get(url, data=json_body, headers=headers)
        data = response.json()
        return data

    def get_futures_limits(self, symbol):
        """Retrieves minimum and maximum order limits for a futures trading pair."""
        timestamp = str(int(time.time() * 1000))
        message = timestamp + self.api_key

        signature = hmac.new(bytes(self.api_secret.encode('utf-8')),
                             msg=bytes(message.encode('utf-8')),
                             digestmod=hashlib.sha256).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'X-ACCESS-KEY': self.api_key,
            'X-ACCESS-TIMESTAMP': timestamp,
            'X-ACCESS-SIGNATURE': signature
        }

        try:
            url = f"https://api.coindcx.com/api/v2/futures/instruments"  # Corrected endpoint
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            instruments_data = response.json()

            for instrument in instruments_data:
                if instrument['symbol'] == symbol:
                    min_quantity = float(instrument['min_quantity'])
                    max_quantity = float(instrument['max_quantity'])

                    print(f"Symbol: {symbol}")
                    print(f"Min Quantity: {min_quantity}")
                    print(f"Max Quantity: {max_quantity}")
                    return min_quantity, max_quantity

            print(f"Symbol {symbol} not found")
            return None, None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching limits: {e}")
            return None, None
        except (KeyError, ValueError) as e:
            print(f"Error parsing response: {e}")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None
    
    def get_active_instruments_details(self, pair, margin_currency_short_name):
        """Fetches active instrument info filtered by margin currency."""
        url = f"https://api.coindcx.com/exchange/v1/derivatives/futures/data/instrument?pair={pair}&margin_currency_short_name={margin_currency_short_name}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("API Response:")
            print(json.dumps(data, indent=4))
            return data
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    def get_epoch_time(self,y):
        """
        year, month, day, hour, minute, second
        Returns the epoch time in seconds for a given date and time in local time.
        """
        return int(pd.Timestamp(year=y[0], month=y[1], day=y[2], hour=y[3], minute=y[4], second=y[5]).timestamp())
        # import 
    def show_Candle(self,pair="B-MKR_USDT",a=[2025,2,1,0,0,0],b=[2025,2,1,0,0,0]):
        url = "https://public.coindcx.com/market_data/candlesticks"

        
        query_params = {
            "pair": pair,
            "from": self.get_epoch_time(a),
            "to": self.get_epoch_time(b),
            "resolution": "60m",  # '1' OR '5' OR '60' OR '1D'
            "pcode": "f"
        }
        response = requests.get(url, params=query_params)
        if response.status_code == 200:
            data = response.json()
            # Process the data as needed
            print(data)
        else:
            print(f"Error: {response.status_code}, {response.text}")


        if response.status_code == 200:
            df = pd.DataFrame(data['data'], columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            fig = go.Figure(data=[go.Candlestick(x=df['time'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'])])
            fig.show()

    def get_candlestick_data(self,pair="B-MKR_USDT",from_timestamp=[2025,2,1,0,0,0],to_timestamp=[2025,2,1,0,0,0],resolution="5m"):

        """Fetches candlestick data from the CoinDCX API."""
        url = "https://public.coindcx.com/market_data/candlesticks"
        query_params = {
            # 'X-AUTH-APIKEY': self.api_key,
            # 'X-AUTH-SIGNATURE': self._generate_signature(self.api_secret),
            "pair": pair,
            "from": self.get_epoch_time(from_timestamp),
            "to": self.get_epoch_time(to_timestamp),
            "resolution": resolution,
            "pcode": "f"  # Or appropriate pcode if needed
        }
        try:
            response = requests.get(url, params=query_params)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            df = pd.DataFrame(data['data'])

            if df.empty:
                print("No data received from the API")
                return None

            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index('time', inplace=True)
            return df

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except (KeyError, TypeError, ValueError) as e:  # Handle potential data errors
            print(f"Error processing data: {e}. Check the API response format.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


    def generate_trading_signals(self,pair, from_date=None, to_date=None, from_timestamp=None, to_timestamp=None, resolution="1m"):
        """Generates trading signals using the 'ta' library."""

        if (from_date and from_timestamp) or (to_date and to_timestamp):
            raise ValueError("Provide either date or timestamp, not both.")

        try:
            if from_date:
                from_timestamp = int(datetime.datetime.strptime(from_date, '%Y-%m-%d').timestamp()) * 1000
            elif not from_timestamp:
                from_timestamp = int((time.time() - 30 * 24 * 60 * 60) * 1000)  # 30 days ago

            if to_date:
                to_timestamp = int(datetime.datetime.strptime(to_date, '%Y-%m-%d').timestamp()) * 1000
            elif not to_timestamp:
                to_timestamp = int(time.time() * 1000)  # Now

            all_data = []
            current_time = datetime.datetime.fromtimestamp(from_timestamp / 1000)  # Start from the from_timestamp
            end_time = datetime.datetime.fromtimestamp(to_timestamp / 1000)

            while current_time < end_time:
                to_time_chunk = current_time + datetime.timedelta(days=1)  # Request 1 day at a time (adjust as needed)
                if to_time_chunk > end_time:
                    to_time_chunk = end_time

                from_ts = int(current_time.timestamp()) * 1000
                to_ts = int(to_time_chunk.timestamp()) * 1000

                data_chunk = self.get_candlestick_data(pair, from_ts, to_ts, resolution)

                if data_chunk is None:
                    return None

                if not data_chunk.empty: #Check if chunk is empty
                    all_data.append(data_chunk)

                current_time = to_time_chunk
                time.sleep(1)  # Rate limiting (adjust as needed)

            if not all_data: # Check if all_data is empty
                print("No data retrieved after chunking")
                return None

            df = pd.concat(all_data)
            df.set_index('time', inplace=True)

            df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)

            df['Buy_Signal'] = (df['RSI_14'] < 30) & (df['MACD_12_26_9'] > df['MACD_signal_12_26_9'])
            df['Sell_Signal'] = (df['RSI_14'] > 70) & (df['MACD_12_26_9'] < df['MACD_signal_12_26_9'])

            return df

        except ValueError as e:
            print(f"Error with date/timestamp: {e}. Use 'YYYY-MM-DD' or timestamps.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None



# import pandas as pd
# import numpy as np

# class TradingBot:
#     def __init__(self, atr_multiplier=1.5):
#         self.atr_multiplier = atr_multiplier

    def get_historical_data(self, pair):
        # Replace this with actual API call
        data = pd.DataFrame({
            "high": np.random.uniform(95, 105, 100),
            "low": np.random.uniform(85, 95, 100),
            "close": np.random.uniform(90, 100, 100),
        })
        return data

    def calculate_atr(self, data, period=14):
        data["tr1"] = data["high"] - data["low"]
        data["tr2"] = abs(data["high"] - data["close"].shift(1))
        data["tr3"] = abs(data["low"] - data["close"].shift(1))
        data["true_range"] = data[["tr1", "tr2", "tr3"]].max(axis=1)
        data["ATR"] = data["true_range"].rolling(window=period).mean()
        return data["ATR"].iloc[-1]

    def calculate_stop_price(self, entry_price, order_side, pair):
        data = self.get_historical_data(pair)
        atr = self.calculate_atr(data)
        stop_distance = atr * self.atr_multiplier
        
        if order_side == "buy":
            return entry_price - stop_distance  # Stop-loss below entry for long
        elif order_side == "sell":
            return entry_price + stop_distance  # Stop-loss above entry for short
        else:
            raise ValueError("Invalid order side. Use 'buy' or 'sell'.")

# # Example Usage
# bot = TradingBot(atr_multiplier=2)  # Use ATR x2 for stop-loss
# entry_price = 100  # Example entry price
# stop_price = bot.calculate_stop_price(entry_price, "buy", "B-XRP_USDT")

# print(f"ATR Stop-Loss Price: {stop_price}")

    def cancel_futures_order(self, order_id):
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        timeStamp = int(round(time.time() * 1000))

        body = {
            "timestamp": timeStamp,
            "id": order_id
        }

        json_body = json.dumps(body, separators=(',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/orders/cancel"
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': api_key,
            'X-AUTH-SIGNATURE': signature
        }

        response = requests.post(url, data=json_body, headers=headers)
        # order
        return response.json()
    

    
    def place_future_order(self,pair="B-XRP_USDT",side="buy",order_type="market_order",leverage=100,price=0,total_quantity=6,stop_price=0):
        price=self.get_current_price(pair)
        # stop_loss=self.a
        # python3
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        # python2
        # secret_bytes = bytes(secret)
        
        # Generating a timestamp
        timeStamp = int(round(time.time() * 1000))
        
        body = {
                "timestamp":timeStamp , # EPOCH timestamp in seconds
                "order": {
                "side": side, # buy OR sell
                "pair":pair, # instrument.string
                "order_type": order_type, # market_order OR limit_order 
                "price": price, #numeric value
            "stop_price": stop_price, #numeric value
                "total_quantity": total_quantity, #numerice value
                "leverage": leverage, #numerice value
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
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        
        response = requests.post(url, data = json_body, headers = headers)
        data = response.json()
        print(data)
        return data
        # hp.save_data("orders",data)

    def cancel_all_open_orders(self):
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        # python2
        # secret_bytes = bytes(secret)
        # Generating a timestamp
        timeStamp = int(round(time.time() * 1000))
        body = {
        "timestamp": timeStamp, # EPOCH timestamp in seconds
        "margin_currency_short_name": ["INR"],
        }
        json_body = json.dumps(body, separators = (',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/positions/cancel_all_open_orders"
        headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': self.api_key,
        'X-AUTH-SIGNATURE': signature
        }
        response = requests.post(url, data = json_body, headers = headers)
        if (response.status_code==200):
            print("successfully close all future order")
        data = response.json()
        print(data)
    def close_all_future_order_position(self,positionID):
        # python3
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        # python2
        # secret_bytes = bytes(secret)
        # Generating a timestamp
        timeStamp = int(round(time.time() * 1000))
        body = {
        "timestamp":timeStamp , # EPOCH timestamp in seconds
        "id": positionID # position.id
        }
        json_body = json.dumps(body, separators = (',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/positions/cancel_all_open_orders_for_position"
        headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': self.api_key,
        'X-AUTH-SIGNATURE': signature
        }
        response = requests.post(url, data = json_body, headers = headers)
        data = response.json()
        if response.status_code==200:
            print("successfully close all future order position")
        print(data)

    def exit_all_postion(self,position_id):
        
        # python3ython2
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        # p
        # secret_bytes = bytes(secret)
        # Generating a timestamp
        timeStamp = int(round(time.time() * 1000))
        body = {
        "timestamp": timeStamp , # EPOCH timestamp in seconds
        "id":position_id
        # "id": "434dc174-6503-4509-8b2b-71b325fe417a" # position.id
        }
        json_body = json.dumps(body, separators = (',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/positions/exit"
        headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': self.api_key,
        'X-AUTH-SIGNATURE': signature
        }
        response = requests.post(url, data = json_body, headers = headers)
        data = response.json()
        if response.status_code==200:
            print("successfully exited all positions")
        print(data)

    def list_futures_orders(self):
        # python3
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        # python2
        # secret_bytes = bytes(secret)
        # Generating a timestamp
        timeStamp = int(round(time.time() * 1000))
        body = {
        
        "timestamp": timeStamp , # EPOCH timestamp in seconds
        "status": "open", # Comma separated statuses as open,filled,cancelled
        "side": "buy", # buy OR sell
        "page": "1", #// no.of pages needed
        "size": "10", #// no.of records needed
        "margin_currency_short_name": ["INR", "USDT"]
        }
        json_body = json.dumps(body, separators = (',', ':'))
        signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
        url = "https://api.coindcx.com/exchange/v1/derivatives/futures/orders"
        headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': self.api_key,
        'X-AUTH-SIGNATURE': signature
        }
        response = requests.post(url, data = json_body, headers = headers)
        data = response.json()
        print(data)
        return data
