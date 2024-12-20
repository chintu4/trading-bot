import os
import logging
from services.coindcx_api import CoinDCXAPI
from strategies.percentage_strategy import PercentageStrategy
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    api_key = os.getenv("COINDCX_API_KEY")
    api_secret = os.getenv("COINDCX_API_SECRET")

    if not api_key or not api_secret:
        logger.error("Please set COINDCX_API_KEY and COINDCX_API_SECRET environment variables.")
        exit(1)

    coindcx_api = CoinDCXAPI(api_key, api_secret)
    percentage_strategy = PercentageStrategy(coindcx_api)
    coin_name="YFIINR"
    # print(coindcx_api.get_current_price(coin_name))
    # print(coindcx_api.get_balance(coin_name))
    # print(coindcx_api.get_balance("INR"))
    balance=float("{:.2f}".format(coindcx_api.get_balance("INR")))/float(coindcx_api.get_current_price(coin_name))
    float("{:.3f}".format(balance))
    coindcx_api.place_order_now(coin_name,0.00013, coindcx_api.get_current_price(coin_name), "buy", "limit_order")
   
    # balance = coindcx_api.get_current_price("SOLINR")

    # print(balance)
    # if balance:
    #     sol_price = coindcx_api.get_current_price("SOLINR")
    #     if sol_price:
    #         quantity = balance / sol_price
    #         coindcx_api.place_order_now("SOLINR", quantity, sol_price, "buy", "limit_order")
    # coindcx_api.get_order_status()
    # print(coindcx_api.get_percentage_change("BTCINR"))
   

    # while True:
    #     try:
    #         # percentage_strategy.execute("BTCINR", 0.01, 2, 2)
    #         print(coindcx_api.get_current_price("BTCINR"))
    #     except KeyboardInterrupt:
    #         logger.info("Exiting")
    #         break
