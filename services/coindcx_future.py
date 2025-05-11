import asyncio
import datetime
import hashlib
import hmac
import json
import logging
import os
import time
import sys
import pandas_ta as pdt

import pandas as pd
import socketio
from ta import add_all_ta_features
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("COINDCX_API_KEY")
api_secret = os.getenv("COINDCX_API_SECRET")

# Configure logging (optional, but very helpful)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Socket.IO setup
socket_endpoint = 'wss://stream.coindcx.com'
sio = socketio.AsyncClient()

# Authentication
secret_bytes = bytes(api_secret, encoding='utf-8')
channel_name = "coindcx"
body = {"channel": channel_name}
json_body = json.dumps(body, separators=(',', ':'))
signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

# Platform compatibility (Windows)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# --- Helper Functions ---

async def join_channel(channel):
    """Joins a specific channel."""
    try:
      await sio.emit('join', {'channelName': channel, 'authSignature': signature, 'apiKey': api_key})
      logger.info(f"Joined channel: {channel}")
    except Exception as e:
      logger.error(f"Error joining channel {channel}: {e}")

async def process_price_change(response):
    """Processes price change events."""
    current_time = datetime.datetime.now()
    logger.info(f"Price Change Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.debug(f"Price Change Response: {response}")  # Use debug level for detailed info
    # ... (Your price change processing logic)

async def process_position_update(response):
    logger.info(f"Position Update: {response['data']}")

async def process_order_update(response):
    logger.info(f"Order Update: {response['data']}")

async def process_balance_update(response):
    logger.info(f"Balance Update: {response['data']}")

async def process_candlestick(response):
    logger.info(f"Candlestick Data: {response['data']}")

async def process_depth_snapshot(response):
    logger.info(f"Depth Snapshot: {response['data']}")

async def process_current_prices_update(response):
    logger.info(f"Current Prices Update: {response['data']}")

async def process_new_trade(response):
    logger.info(f"New Trade: {response['data']}")

# --- Socket.IO Event Handlers ---

@sio.event
async def connect():
    logger.info("Connected to the server!")
    await join_channel("coindcx")  # Join the main channel
    await join_channel("B-ID_USDT@prices-futures") #Join price update channel
    # ... (Join other channels as needed)

@sio.on('price-change')
async def on_price_change(response):
    await process_price_change(response)

@sio.on('df-position-update')
async def on_position_update(response):
    await process_position_update(response)

@sio.on('df-order-update')
def on_order_update(response):
    process_order_update(response) #No need to await here as it is not a coroutine

@sio.on('balance-update')
def on_balance_update(response):
    process_balance_update(response) #No need to await here as it is not a coroutine

@sio.on('candlestick')
def on_candlestick(response):
    process_candlestick(response) #No need to await here as it is not a coroutine

@sio.on('depth-snapshot')
def on_depth_snapshot(response):
    process_depth_snapshot(response) #No need to await here as it is not a coroutine

@sio.on('currentPrices@futures#update')
def on_current_prices_update(response):
    process_current_prices_update(response) #No need to await here as it is not a coroutine

@sio.on('new-trade')
def on_new_trade(response):
    process_new_trade(response) #No need to await here as it is not a coroutine


async def main():
    try:
        await sio.connect(socket_endpoint, transports='websocket')
        print("socket connected")
        await sio.wait()  # Keep the connection alive
        while True:
            await sio.emit('candlestick', {'symbol': 'B-ID_USDT', 'interval': '1m', 'limit': '1'})
            # print(a)
            await asyncio.sleep(5)



    except Exception as e:
        logger.exception(f"Error connecting to the server: {e}")  # Log the full traceback
        raise  # Re-raise for visibility

    except KeyboardInterrupt as e:
        await sio.disconnect()
        print(e)
        logger.info("Ctrl-C caught. Exiting.")
        await sio.disconnect()

if __name__ == '__main__':

    asyncio.run(main())