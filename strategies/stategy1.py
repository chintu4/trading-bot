import ccxt
import pandas as pd
import numpy as np
import time
import os
import dotenv

from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
# dotenv.load(dotenv_path=env_path)
dotenv.load_dotenv(dotenv_path=env_path)

import ccxt
import pandas as pd
import numpy as np
import time
import os
import dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
dotenv.load_dotenv(dotenv_path=env_path)


class TradingBot:
    def __init__(self, api_key, api_secret, symbol='ETH/USDT', timeframe='1h', trade_amount=0.05, leverage=5):
        # Initialize API keys and exchange
        self.exchange = ccxt.coindcx({
            'apiKey': os.getenv("COINDCX_API_KEY"),
            'secret': os.getenv("COINDCX_API_SECRET"),
            'enableRateLimit': True
        })
        
        # Trading Parameters
        self.symbol = symbol
        self.timeframe = timeframe
        self.trade_amount = trade_amount
        self.leverage = leverage
        
        # Strategy Parameters
        self.short_length = 12
        self.long_length = 21
        self.stop_loss_percent = 4
        self.take_profit_percent = 5
        self.rsi_length = 17
        self.rsi_overbought = 70
        self.rsi_oversold = 26
        self.atr_length = 14
        self.bb_length = 20

    # Fetch Historical Data
    def fetch_data(self, limit=200):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Data Fetch Error: {e}")
            return None

    # Apply Technical Indicators
    def apply_indicators(self, df):
        df['short_sma'] = df['close'].rolling(window=self.short_length).mean()
        df['long_sma'] = df['close'].rolling(window=self.long_length).mean()

        # RSI Calculation
        delta = df['close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=self.rsi_length).mean()
        avg_loss = pd.Series(loss).rolling(window=self.rsi_length).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=self.bb_length).mean()
        df['bb_std'] = df['close'].rolling(window=self.bb_length).std()
        df['bb_upper'] = df['bb_middle'] + (2 * df['bb_std'])
        df['bb_lower'] = df['bb_middle'] - (2 * df['bb_std'])

        # ATR (Average True Range)
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift())
        df['low_close'] = abs(df['low'] - df['close'].shift())
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['true_range'].rolling(window=self.atr_length).mean()

        return df

    # Set Leverage for Futures Trading
    def set_leverage(self):
        try:
            self.exchange.set_leverage(self.leverage, self.symbol)
            print(f"Leverage set to {self.leverage}x for {self.symbol}")
        except Exception as e:
            print(f"Leverage Error: {e}")

    # Execute Trades
    def place_order(self, order_type):
        try:
            if order_type == 'buy':
                self.exchange.create_market_buy_order(self.symbol, self.trade_amount)
                print(f"BUY Order Executed: {self.trade_amount} of {self.symbol}")
            elif order_type == 'sell':
                self.exchange.create_market_sell_order(self.symbol, self.trade_amount)
                print(f"SELL Order Executed: {self.trade_amount} of {self.symbol}")
        except Exception as e:
            print(f"Order Execution Error: {e}")

    # Strategy Logic
    def strategy(self, df):
        last_row = df.iloc[-1]
        entry_price = last_row['close']
        stop_loss = entry_price - (last_row['atr'] * 1.5)
        take_profit = entry_price * (1 + self.take_profit_percent / 100)

        # **Strategy 1: SMA Crossover with RSI**
        if last_row['short_sma'] > last_row['long_sma'] and last_row['rsi'] < self.rsi_overbought:
            self.place_order('buy')

        if last_row['short_sma'] < last_row['long_sma'] and last_row['rsi'] > self.rsi_oversold:
            self.place_order('sell')

        # **Strategy 2: Bollinger Bands Mean Reversion**
        if last_row['close'] < last_row['bb_lower'] and last_row['rsi'] < self.rsi_oversold:
            self.place_order('buy')

        if last_row['close'] > last_row['bb_upper'] and last_row['rsi'] > self.rsi_overbought:
            self.place_order('sell')

        # **Strategy 3: ATR Stop Loss**
        print(f"Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}")


    # Run the Bot
    def run(self):
        self.set_leverage()
        while True:
            data = self.fetch_data()
            if data is not None:
                data = self.apply_indicators(data)
                self.strategy(data)
            time.sleep(3600)  # Run every hour


# Instantiate and Run the Bot
if __name__ == "__main__":
    bot = TradingBot(
        api_key=os.getenv("COINDCX_API_KEY"),
        api_secret=os.getenv("COINDCX_API_SECRET"),
        symbol="ETH/USDT",
        timeframe="1h",
        trade_amount=0.05,
        leverage=5
    )
    bot.run()
