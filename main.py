
import requests

class ExchangeAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            # Add other required headers here
        }

    def get_market_data(self, symbol):
        raise NotImplementedError("This method should be overridden by subclasses.")

class CoinDCXAPI(ExchangeAPI):
    BASE_URL = "https://api.coindcx.com"

    def get_market_data(self, symbol):
        endpoint = f"/exchange/v1/market_details?symbol={symbol}"
        url = self.BASE_URL + endpoint

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return {
                "last_price": float(data["market_details"]["last_price"]),
                # Add other relevant data fields as needed
            }

        except requests.exceptions.RequestException as e:
            print(f"Error fetching market data for {symbol}: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing response for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for {symbol}: {e}")
            return None

    def get_latest_price(self, symbol):
        market_data = self.get_market_data(symbol)
        if market_data:
            return market_data['last_price']
        else:
            return None