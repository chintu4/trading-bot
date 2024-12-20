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
    # print(coindcx_api.get_current_price("BAXINR"))
    # print(coindcx_api.get_balance("BAXINR"))
    # coindcx_api.place_order_now("BAXINR", 10066, coindcx_api.get_current_price("BAXINR"), "sell", "limit_order")
    # coindcx_api.get_order_status()
    print(coindcx_api.get_percentage_change("BTCINR"))
   

    # while True:
    #     try:
    #         # percentage_strategy.execute("BTCINR", 0.01, 2, 2)
    #         print(coindcx_api.get_current_price("BTCINR"))
    #     except KeyboardInterrupt:
    #         logger.info("Exiting")
    #         break
