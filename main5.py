import requests
import pandas as pd
import time
import hmac
import hashlib
import ta  # for technical analysis indicators
import json
import os
from dotenv import load_dotenv
load_dotenv(".env")
from services.coindcx_api import CoinDCXAPI
# Define API keys from .env file
API_KEY = os.getenv("COINDCX_API_KEY")
API_SECRET = os.getenv("COINDCX_API_SECRET")

# Define CoinDCX API base URL
BASE_URL = 'https://api.coindcx.com'

# Paper trading variables
paper_balance = 1000  # USD balance for paper trading
position = 0  # Current position (0 means no position)

# Function to get market data


# Add technical indicators to the DataFrame
def add_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['macd'] = ta.trend.MACD(df['close']).macd()
    df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
    return df

# Define buy/sell signals based on RSI and SMA
def generate_signals(df):
    df['buy_signal'] = (df['rsi'] < 30) & (df['close'] > df['sma_50'])
    df['sell_signal'] = (df['rsi'] > 70) & (df['close'] < df['sma_50'])
    return df

from datetime import datetime

# Get current time
now = datetime.now()

# Convert to array [year, month, day, hour, minute, second]
time_array = [now.year, now.month, now.day, now.hour, now.minute, now.second]

print(time_array)

# Simulate placing a paper trade order
def place_order(symbol, side, quantity, price=None):
    global paper_balance, position

    # Paper trading logic - simulate buy/sell
    if side == 'buy':
        cost = quantity * price
        if paper_balance >= cost:  # Check if there's enough balance
            paper_balance -= cost
            position += quantity
            print(f"BUY {quantity} {symbol} at {price} | Balance: {paper_balance} USD")
        else:
            print("Not enough balance to buy")
    elif side == 'sell':
        if position >= quantity:  # Check if position has the asset
            revenue = quantity * price
            paper_balance += revenue
            position -= quantity
            print(f"SELL {quantity} {symbol} at {price} | Balance: {paper_balance} USD")
        else:
            print("Not enough position to sell")

# Track profit/loss
def calculate_pnl(entry_price, quantity, current_price):
    return (current_price - entry_price) * quantity

# Main loop for paper trading
def paper_trading(symbol='BTCUSDT',timear=time_array):
    global paper_balance, position
    cdcx=CoinDCXAPI()
    
    while True:
        # Fetch market data
        df = cdcx.get_candlestick_data(pair=symbol,from_timestamp=[2025,2,2,0,0,0],to_timestamp=timear)
        if df.empty:
            print("No market data fetched, skipping iteration.")
            continue  # Skip this iteration if no data

        df = add_indicators(df)
        df = generate_signals(df)
        
        latest_data = df.iloc[-1]  # Get the latest row
        
        print(f"Latest Data: {latest_data[['close', 'rsi', 'macd', 'sma_50']]}")

        # Execute paper trading based on signals
        if latest_data['buy_signal']:
            print("Buy Signal detected!")
            if position == 0:  # Ensure no position before buying
                quantity_to_buy = 0.01  # Example quantity
                place_order(symbol, 'buy', quantity_to_buy, latest_data['close'])

        elif latest_data['sell_signal']:
            print("Sell Signal detected!")
            if position > 0:  # Ensure there's a position before selling
                quantity_to_sell = 0.01  # Example quantity
                place_order(symbol, 'sell', quantity_to_sell, latest_data['close'])

        # Print status every iteration
        print(f"Paper Balance: {paper_balance} USD | Position: {position} {symbol}")
        print("-"*50)
        
        # Wait for 1 minute before checking again
        time.sleep(1)  # 60 seconds for 1-minute candle intervals

# Start paper trading simulation
if __name__ == "__main__":
    paper_trading(symbol='B-SOL_USDT')
