# from strategy1 import CoinDCXFuturesBot
from stategy1 import CoinDCXBot, CoinDCXFuturesBot
import time
import ccxt
import os
import pandas as pd
import numpy as np
import dotenv
from pathlib import Path


env_path = Path(__file__).resolve().parent.parent / '.env'
# dotenv.load(dotenv_path=env_path)
dotenv.load_dotenv(dotenv_path=env_path)
# api_key = os.getenv("COINDCX_API_KEY")
# api_secret = os.getenv("COINDCX_API_SECRET")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

api_key = os.getenv("COINDCX_API_KEY")
api_secret = os.getenv("COINDCX_API_SECRET")



class PaperTradingBot(CoinDCXFuturesBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.virtual_balance = 1000  # Starting virtual balance
        self.virtual_positions = 0  # No positions initially
        
    def place_order(self, order_type):
        if order_type == 'buy':
            self.virtual_positions = self.virtual_balance / self.last_price * self.leverage
            print(f"Simulated Buy (Long) at {self.last_price}")
        elif order_type == 'sell' and self.virtual_positions > 0:
            profit = (self.virtual_positions * self.last_price) - self.virtual_balance
            self.virtual_balance += profit
            self.virtual_positions = 0
            print(f"Simulated Sell (Short) at {self.last_price} Profit: {profit}")
        
    def simulate(self):
        while True:
            data = self.fetch_data()
            data = self.apply_indicators(data)
            self.last_price = data.iloc[-1]['close']
            self.strategy(data)
            print(f"Virtual Balance: {self.virtual_balance}")
            time.sleep(3600)


class Backtester:
    def __init__(self, api_key=api_key, api_secret=api_secret, symbol='ETH/USDT', timeframe='1h', short_length=12, long_length=21, rsi_length=17, leverage=10):
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbol = symbol
        self.timeframe = timeframe
        self.short_length = short_length
        self.long_length = long_length
        self.rsi_length = rsi_length
        self.leverage = leverage
        
        self.exchange = ccxt.coindcx({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True
        })
        
    def fetch_data(self, limit=1000):
        # Fetch historical data from CoinDCX
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def apply_indicators(self, df):
        # Calculate short and long SMA
        df['short_sma'] = df['close'].rolling(window=self.short_length).mean()
        df['long_sma'] = df['close'].rolling(window=self.long_length).mean()
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=self.rsi_length).mean()
        avg_loss = pd.Series(loss).rolling(window=self.rsi_length).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def simulate_trades(self, df):
        # Simulate the trades and calculate performance
        balance = 1000  # Starting balance in USD
        position = 0  # No open positions initially
        entry_price = 0
        total_profit = 0
        for index, row in df.iterrows():
            # Buy signal
            if row['short_sma'] > row['long_sma'] and row['rsi'] < 70 and position == 0:
                position = balance / row['close'] * self.leverage
                entry_price = row['close']
                print(f"Buying at {row['close']} on {row['timestamp']}")
                
            # Sell signal
            if row['short_sma'] < row['long_sma'] and row['rsi'] > 30 and position > 0:
                balance = position * row['close']  # Sell at the current price
                profit = balance - (position * entry_price)
                total_profit += profit
                position = 0
                print(f"Selling at {row['close']} on {row['timestamp']} Profit: {profit}")
        
        # Final Balance
        if position > 0:
            balance = position * df.iloc[-1]['close']
        return balance, total_profit
    
    def backtest(self):
        data = self.fetch_data(limit=1000)  # Fetch historical data
        data = self.apply_indicators(data)
        final_balance, total_profit = self.simulate_trades(data)
        print(f"Final Balance: {final_balance}, Total Profit: {total_profit}")
        


    
    def paper_trading(self):
        # Start a paper trading session
        balance = 1000  # Starting balance in USD
        position = 0  # No open positions initially
        entry_price = 0
        total_profit = 0
        while True:
            data = self.fetch_data(limit=1)  # Fetch the latest data
            data = self.apply_indicators(data)
            row = data.iloc[-1]
            # Buy signal
            if row['short_sma'] > row['long_sma'] and row['rsi'] < 70 and position == 0:
                position = balance / row['close'] * self.leverage
                entry_price = row['close']
                print(f"Buying at {row['close']} on {row['timestamp']}")
                
            # Sell signal
            if row['short_sma'] < row['long_sma'] and row['rsi'] > 30 and position > 0:
                balance = position * row['close']  # Sell at the current price
                profit = balance - (position * entry_price)
                total_profit += profit
                position = 0
                print(f"Selling at {row['close']} on {row['timestamp']} Profit: {profit}")
            
            print(f"Current Balance: {balance}, Total Profit: {total_profit}")
            time.sleep(60)  # Run every minute

    def test_strategy1(self):
        # Test Strategy 1 using paper trading
            # Print the current balance and total profit
        strategy1_bot = CoinDCXBot(api_key=self.api_key, api_secret=self.api_secret, symbol='ETH/USDT', timeframe='1h', trade_amount=0.05, leverage=10)
            # Wait for 1 minute
        time.sleep(60)
        
        strategy1_bot.sunmore()

test=Backtester()
test.test_strategy1()
