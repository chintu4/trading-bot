import socketio
import hmac
import hashlib
import json
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
key = os.getenv("COINDCX_API_KEY")
secret = os.getenv("COINDCX_API_SECRET")

socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.Client()
sio.connect(socketEndpoint, transports = 'websocket')
# key = "XXXX"
# secret = "YYYY"
# python3
secret_bytes = bytes(secret, encoding='utf-8')
# python2
# secret_bytes = bytes(secret)
body = {"channel":"coindcx"}
json_body = json.dumps(body, separators = (',', ':'))
signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
# Join channel
sio.emit('join', { 'channelName': 'coindcx', 'authSignature': signature, 'apiKey' : key })


# @sio.on("candlestick")
# def candlestick(response):
#     print(response["data"])
# @sio.event
# def candlestick(response):
#     print(response["data"])

# @sio.connect()

@sio.on('candlestick')
def on_message(response):
    print(response)
    print("candlestick worked")


a=sio.emit("candlestick",{'symbol': 'B-ID_USDT', 'interval': '1m', 'limit': '1'})
print(a)
print("code ended")
# sio.emit('leave', { 'channelName' : 'coindcx' })