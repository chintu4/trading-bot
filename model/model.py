import numpy as np
import pandas as pd
from services.coindcx_api import CoinDCXAPI
import ccxt
import time

class BacktestModel:
    def __init__(self, historical_data, initial_balance):
        self.historical_data = historical_data
        self.balance = initial_balance
        self.position = 0  # 0 means no position, 1 means holding

    def backtest(self):
        for index, row in self.historical_data.iterrows():
            current_price = row['price']
            signal = self.generate_signal(row)
            
            if signal == 'buy' and self.position == 0:
                self.buy(current_price)
            elif signal == 'sell' and self.position == 1:
                self.sell(current_price)

    def generate_signal(self, data_row):
        # Simple strategy: buy if price is lower than a threshold, sell if higher
        buy_threshold = 100
        sell_threshold = 120
        if data_row['price'] < buy_threshold:
            return 'buy'
        elif data_row['price'] > sell_threshold:
            return 'sell'
        return 'hold'

    def buy(self, price):
        self.position = 1
        print(f"Bought at {price}")

    def sell(self, price):
        self.position = 0
        print(f"Sold at {price}")

# Example usage:
# Assuming `historical_data` is a DataFrame with a 'price' column
# historical_data = pd.DataFrame({'price': [95, 101, 115, 108, 125]})
# model = BacktestModel(historical_data, initial_balance=1000)
# model.backtest()

    @classmethod
    def backtest_symbol(cls, symbol, initial_balance, from_time, to_time):
        coindcx_api = CoinDCXAPI()
        historical_data = coindcx_api.get_historical_data(symbol, from_time, to_time)
        model = cls(historical_data, initial_balance)
        model.backtest()
        return model



# CoinDCX API Keys
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Initialize CoinDCX
exchange = ccxt.coindcx({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True
})

# Strategy Parameters
SHORT_LENGTH = 12
LONG_LENGTH = 21
STOP_LOSS_PERCENT = 4
TAKE_PROFIT_PERCENT = 5
RSI_LENGTH = 17
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 26
SYMBOL = 'ETH/USDT'
TIMEFRAME = '1h'
TRADE_AMOUNT = 0.05  # Trade amount in ETH

# Fetch Historical Data
def fetch_data(symbol, timeframe, limit=200):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Calculate Indicators
def apply_indicators(df):
    df['short_sma'] = df['close'].rolling(window=SHORT_LENGTH).mean()
    df['long_sma'] = df['close'].rolling(window=LONG_LENGTH).mean()
    
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=RSI_LENGTH).mean()
    avg_loss = pd.Series(loss).rolling(window=RSI_LENGTH).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

# Execute Trades
def place_order(order_type, amount):
    try:
        if order_type == 'buy':
            exchange.create_market_buy_order(SYMBOL, amount)
            print(f"Buy Order Executed for {amount} ETH")
        elif order_type == 'sell':
            exchange.create_market_sell_order(SYMBOL, amount)
            print(f"Sell Order Executed for {amount} ETH")
    except Exception as e:
        print(f"Order Error: {e}")

# Trading Logic
def strategy(df):
    last_row = df.iloc[-1]
    entry_price = last_row['close']
    stop_loss = entry_price * (1 - STOP_LOSS_PERCENT / 100)
    take_profit = entry_price * (1 + TAKE_PROFIT_PERCENT / 100)

    # Buy Condition
    if last_row['short_sma'] > last_row['long_sma'] and last_row['rsi'] < RSI_OVERBOUGHT:
        place_order('buy', TRADE_AMOUNT)

    # Sell Condition
    if last_row['short_sma'] < last_row['long_sma'] and last_row['rsi'] > RSI_OVERSOLD:
        place_order('sell', TRADE_AMOUNT)

    print(f"Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}")

# Main Loop
while True:
    data = fetch_data(SYMBOL, TIMEFRAME)
    data = apply_indicators(data)
    strategy(data)
    time.sleep(3600)  # Run every hour
