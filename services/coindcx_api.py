import requests
import logging
import hmac
import hashlib
import time
import json
from services.exchange_api import ExchangeAPI

class CoinDCXAPI(ExchangeAPI):
    BASE_URL = "https://api.coindcx.com"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
    
    def get_current_price(self,pair):
        """"
        # Example usage
pair = "SOLINR"  # Replace with your desired market pair
price = get_current_price(pair)
if price:
    print(f"The current price of {pair} is {price}")
else:
    print(f"Price for {pair} not found")
        """  
              
        url = f"https://api.coindcx.com/exchange/ticker"
        response = requests.get(url)
        data = response.json()

        for item in data:
            if item['market'] == pair:
                return item['last_price']
        return None
    

   

    def get_latest_price(self, symbol):
        endpoint = f"/exchange/v1/market_details?symbol={symbol}"
        url = self.BASE_URL + endpoint

        try:
            response = requests.get(url, timeout=10)  # Add a timeout
            response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)

            data = response.json()

            if "market_details" not in data or "last_price" not in data["market_details"]:
                # Log the entire response for debugging
                logging.error("Unexpected API response structure: %s", data)
                raise KeyError("Expected 'market_details' or 'last_price' key missing")

            return float(data["market_details"]["last_price"])

        except requests.exceptions.RequestException as e:
            logging.error("Error during API request: %s", e)
            return None
        except KeyError as e:
            logging.error("Error processing the response: %s", e)
            return None
        except Exception as e:
            logging.error("An unexpected error occurred: %s", e)
            return None

# # Example usage
# api = CoinDCXAPI()
# symbol = "BTCINR"  # Replace with your desired symbol
# price = api.get_latest_price(symbol)
# if price:
#     print(f"The current price of {symbol} is {price}")
# else:
#     print(f"Price for {symbol} not found")

    def place_order(self, symbol, quantity, price, order_side, order_type):
        # Implement CoinDCX-specific order placement logic here
        # This would likely involve authentication and sending a POST request
        # with relevant order parameters
        raise NotImplementedError("Order placement not implemented yet.")
    # import requests




    def _generate_signature(self, payload):
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        signature = hmac.new(secret_bytes, payload.encode(), hashlib.sha256).hexdigest()
        return signature

    # def place_order(self, symbol, quantity, price, order_side, order_type):
    #     endpoint = "/exchange/v1/orders/create"
    #     url = self.BASE_URL + endpoint

    #     timestamp = int(time.time() * 1000)
    #     payload = {
    #         "market": symbol,
    #         "total_quantity": quantity,
    #         "price_per_unit": price,
    #         "side": order_side,
    #         "order_type": order_type,
    #         "timestamp": timestamp
    #     }
    #     json_payload = json.dumps(payload, separators=(',', ':'))
    #     signature = self._generate_signature(json_payload)

    #     headers = {
    #         "Content-Type": "application/json",
    #         "X-AUTH-APIKEY": self.api_key,
    #         "X-AUTH-SIGNATURE": signature
    #     }

    #     try:
    #         response = requests.post(url, data=json_payload
                                     

#     def get_balance(self, symbol):
#         endpoint = "/exchange/v1/users/balances"
#         url = self.BASE_URL + endpoint

#         timestamp = int(time.time() * 1000)
#         payload = {
#             "timestamp": timestamp
#         }
#         json_payload = json.dumps(payload, separators=(',', ':'))
#         signature = self._generate_signature(json_payload)

#         headers = {
#             "Content-Type": "application/json",
#             "X-AUTH-APIKEY": self.api_key,
#             "X-AUTH-SIGNATURE": signature
#         }

#         try:
#             response = requests.post(url, data=json_payload, headers=headers)
#             response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
#             balances = response.json()
#             for balance in balances:
#                 if balance['currency'] == symbol:
#                     return float(balance['balance'])
#             return None
#         except requests.exceptions.RequestException as e:
#             print(f"Error during API request: {e}")
#             return None
# # import requests
# # import hmac
# # import hashlib
# # import time
# # import json

# # class CoinDCXAPI:
# #     BASE_URL = "https://api.coindcx.com"

# #     def __init__(self, api_key, api_secret):
# #         self.api_key = api_key
# #         self.api_secret = api_secret

# #     def _generate_signature(self, payload):
# #         secret_bytes = bytes(self.api_secret, encoding='utf-8')
# #         signature = hmac.new(secret_bytes, payload.encode(), hashlib.sha256).hexdigest()
# #         return signature

    # def get_balance(self, symbol):
    #     endpoint = "/exchange/v1/users/balances"
    #     url = self.BASE_URL + endpoint

    #     timestamp = int(time.time() * 1000)
    #     payload = {
    #         "timestamp": timestamp
    #     }
    #     json_payload = json.dumps(payload, separators=(',', ':'))
    #     signature = self._generate_signature(json_payload)

    #     headers = {
    #         "Content-Type": "application/json",
    #         "X-AUTH-APIKEY": self.api_key,
    #         "X-AUTH-SIGNATURE": signature
    #     }

    #     try:
    #         response = requests.post(url, data=json_payload, headers=headers)
    #         response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
    #         balances = response.json()
    #         for balance in balances:
    #             if balance['currency'] == symbol:
    #                 return float(balance['balance'])
    #         return None
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error during API request: {e}")
    #         return None

    def place_order_percentage(self, symbol, percentage, price, order_side, order_type):
        balance = self.get_balance(symbol)
        if balance is None:
            print(f"Could not retrieve balance for {symbol}")
            return None

        quantity = balance * (percentage / 100)

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
            response = requests.post(url, data=json_payload, headers=headers)
            response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None
#         import requests
# import hmac
# import hashlib
# import time
# import json

# class CoinDCXAPI:
#     BASE_URL = "https://api.coindcx.com"

#     def __init__(self, api_key, api_secret):
#         self.api_key = api_key
#         self.api_secret = api_secret

#     def _generate_signature(self, payload):
#         secret_bytes = bytes(self.api_secret, encoding='utf-8')
#         signature = hmac.new(secret_bytes, payload.encode(), hashlib.sha256).hexdigest()
#         return signature

    def get_balance(self, symbol):
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

# # Example usage
# api_key = "your_api_key"
# api_secret = "your_api_secret"
# api = CoinDCXAPI(api_key, api_secret)

# symbol = "BTC"  # Replace with your desired symbol
# balance = api.get_balance(symbol)
# if balance is not None:
#     print(f"Your current holdings of {symbol} are {balance}")
# else:
#     print(f"Could not retrieve balance for {symbol}")


# # Example usage
# api_key = "your_api_key"
# api_secret = "your_api_secret"
# api = CoinDCXAPI(api_key, api_secret)

# symbol = "BTCINR"  # Replace with your desired symbol
# percentage = 10  # Replace with the percentage of your holdings you want to sell
# price = 5000000  # Replace with your desired price
# order_side = "sell"  # Replace with "buy" or "sell"
# order_type = "limit_order"  # Replace with "limit_order" or "market_order"

# order_response = api.place_order(symbol, percentage, price, order_side, order_type)
# print(order_response)

# import requests
# import hmac
# import hashlib
# import time
# import json

# class CoinDCXAPI:
#     BASE_URL = "https://api.coindcx.com"

#     def __init__(self, api_key, api_secret):
#         self.api_key = api_key
#         self.api_secret = api_secret

#     def _generate_signature(self, payload):
#         secret_bytes = bytes(self.api_secret, encoding='utf-8')
#         signature = hmac.new(secret_bytes, payload.encode(), hashlib.sha256).hexdigest()
#         return signature

    def place_order_quantity(self, symbol, quantity, price, order_side, order_type):
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
            response = requests.post(url, data=json_payload, headers=headers)
            response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None

# # Example usage
# api_key = "your_api_key"
# api_secret = "your_api_secret"
# api = CoinDCXAPI(api_key, api_secret)

# symbol = "BTCINR"  # Replace with your desired symbol
# quantity = 0.01  # Replace with your desired quantity
# price = 5000000  # Replace with your desired price
# order_side = "buy"  # Replace with "buy" or "sell"
# order_type = "limit_order"  # Replace with "limit_order" or "market_order"

# order_response = api.place_order(symbol, quantity, price, order_side, order_type)
# print(order_response)

# import requests
# import hmac
# import hashlib
# import time
# import json

# class CoinDCXAPI:
#     BASE_URL = "https://api.coindcx.com"

#     def __init__(self, api_key, api_secret):
#         self.api_key = api_key
#         self.api_secret = api_secret

#     def _generate_signature(self, payload):
#         secret_bytes = bytes(self.api_secret, encoding='utf-8')
#         signature = hmac.new(secret_bytes, payload.encode(), hashlib.sha256).hexdigest()
#         return signature

    def place_order_now(self, symbol, quantity, price, order_side, order_type):
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
            response = requests.post(url, data=json_payload, headers=headers) 
            response.raise_for_status() # Check for HTTP errors (4xx or 5xx) 
            order_data = response.json() 
            return order_data.get("id") # Retrieve the order ID from the response 
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            print("Response content:", response.content)  # Log the full response content
            return None

# # Example usage
# api_key = "your_api_key"
# api_secret = "your_api_secret"
# api = CoinDCXAPI(api_key, api_secret)

# symbol = "BTCINR"  # Replace with your desired symbol
# quantity = 0.01  # Replace with your desired quantity
# price = 5000000  # Replace with your desired price
# order_side = "buy"  # Replace with "buy" or "sell"
# order_type = "limit_order"  # Replace with "limit_order" or "market_order"

# order_response = api.place_order(symbol, quantity, price, order_side, order_type)
# print(order_response)

# import requests
# import hmac
# import hashlib
# import time
# import json

# class CoinDCXAPI:
#     BASE_URL = "https://api.coindcx.com"

#     def __init__(self, api_key, api_secret):
#         self.api_key = api_key
#         self.api_secret = api_secret

#     def _generate_signature(self, payload):
#         secret_bytes = bytes(self.api_secret, encoding='utf-8')
#         signature = hmac.new(secret_bytes, payload.encode(), hashlib.sha256).hexdigest()
#         return signature

    def get_order_status(self, order_id):
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
            response = requests.post(url, data=json_payload, headers=headers)
            response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None

# # Example usage
# api_key = "your_api_key"
# api_secret = "your_api_secret"
# coindcx_api = CoinDCXAPI(api_key, api_secret)

# order_id = "your_order_id"  # Replace with your actual order ID
# order_status = coindcx_api.get_order_status(order_id)
# print(order_status)

# import requests

# class CoinDCXAPI:
#     BASE_URL = "https://api.coindcx.com"

#     def get_current_price(self, symbol):
#         url = f"{self.BASE_URL}/exchange/ticker"
#         response = requests.get(url)
#         data = response.json()
        
#         for item in data:
#             if item['market'] == symbol:
#                 return float(item['last_price'])
#         return None

    def get_percentage_change(self, symbol):
        url = f"{self.BASE_URL}/exchange/ticker"
        response = requests.get(url)
        data = response.json()
        
        for item in data:
            if item['market'] == symbol:
                current_price = float(item['last_price'])
                change_24_hour = float(item['change_24_hour'])
                previous_price = current_price / (1 + change_24_hour / 100)
                percentage_change = ((current_price - previous_price) / previous_price) * 100
                return percentage_change
        return None

# # Example usage
# api = CoinDCXAPI()
# symbol = "BTCINR"  # Replace with your desired market pair
# percentage_change = api.get_percentage_change(symbol)
# if percentage_change is not None:
#     print(f"The percentage change for {symbol} is {percentage_change:.2f}%")
# else:
#     print(f"Could not retrieve percentage change for {symbol}")

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

# # Example usage
# quantity = 10066  # Replace with the quantity you want to sell
# price_per_unit = 5000000  # Replace with the current price per unit
# platform_fee_percentage = 0.2  # Replace with the platform fee percentage
# gst_percentage = 18  # Replace with the GST percentage

# total_cost = calculate_total_cost_after_selling(quantity, price_per_unit, platform_fee_percentage, gst_percentage)
# print(f"The total cost after selling {quantity} units is {total_cost}")


#TODO : add function to get back tested
