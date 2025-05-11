import os
import logging
from services.coindcx_api import CoinDCXAPI
from strategies.percentage_strategy import PercentageStrategy
from strategies.stategy1 import TradingBot
import time
from datetime import datetime
import Telegram.bot as telegram
import numpy as np
import pandas as pd
import json
from dotenv import load_dotenv
load_dotenv()




# apply not indicator stategy
if __name__ == "__main__":
    ex=CoinDCXAPI()
    ps=PercentageStrategy()
    
    
    



@app.event_grid_trigger(arg_name="azeventgrid")
def EventGridTrigger(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event')
