import socketio
import pandas as pd
import pandas_ta as pdta
import json
import time
from strategies.percentage_strategy import PercentageStrategy
from services.coindcx_api import CoinDCXAPI

coindcx=CoinDCXAPI()
perSta=PercentageStrategy(coindcx,"C:/Users/dsjapnc/Documents/chintu Sharma/trading Pratform/data/PerSta.csv")




def cal_take_profit(cupr, reward_percentage):
    """
    Calculate the take profit price.
    :param cupr: Current price of the asset
    :param reward_percentage: Percentage gain to take profit (e.g., 0.05 for 5%)
    :return: Take profit price
    """

    """
    implement traling profit
    implement if profit abot
    """
    return cupr + (cupr * reward_percentage)

def cal_stop_loss(cupr, risk_percentage):
    """
    Calculate the stop loss price.
    :param cupr: Current price of the asset
    :param risk_percentage: Percentage drop to set stop loss (e.g., 0.02 for 2%)
    :return: Stop loss price
    """
    return cupr - (cupr * risk_percentage)


socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.Client()
instrument = "B-BTC_USDT_1m"

# Define future pairs and spot pairs
futurePair = ["B-ID_USDT@prices-futures"]
sportPair = ["B-BTC_USDT_1m", "B-BTC_USDT_1m"]

# Simple Strategy: Moving Average Crossover with RSI and MACD
short_window = 9  # 9-period MA for short-term signal
long_window = 21  # 21-period MA for long-term signal
rsi_period = 14  # 14-period RSI
macd_fast = 12  # MACD fast window
macd_slow = 26  # MACD slow window
macd_signal = 9  # MACD signal window

# Data frame for storing price data
price_data = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Risk Management parameters
stop_loss_percentage = 0.02  # 2% stop loss
take_profit_percentage = 0.04  # 4% take profit
trailing_stop_percentage = 0.02  # 2% trailing stop
account_balance = 1000  # Example account balance in USDT

# Placeholder for the last order (for example purpose)
last_order = None
last_order_price = None
position_size = None
entry_price = None
max_price_since_entry = None  # Used for trailing stop calculation

# Backtesting parameters
backtest = False
historical_data = pd.read_csv("historical_btc_data.csv")  # Replace with your historical data
backtest_results = []

@sio.event
def connect():
    print("I'm connected!")
    sio.emit('join', {'channelName': instrument})

@sio.on('candlestick')
def on_message(response):
    global price_data, last_order, last_order_price, entry_price, max_price_since_entry, position_size

    # Convert incoming response into DataFrame
    df = convert_pd(response)
    
    # Append new data to the DataFrame
    price_data = pd.concat([price_data, df], ignore_index=True)
    
    # Limit the size of the data to the size of the longest window
    if len(price_data) > long_window:
        price_data = price_data.tail(long_window)
    
    print(f"Price Data (last {len(price_data)} rows):\n{price_data.tail()}")
    
    # Check for trading signal
    signal = check_signal(price_data)
    
    if signal == 'buy' and last_order != 'buy':
        print("Buy Signal Triggered!")
        position_size = calculate_position_size()
        place_order('buy')
        entry_price = price_data['close'].iloc[-1]
        max_price_since_entry = entry_price  # Initial max price is entry price
    elif signal == 'sell' and last_order != 'sell':
        print("Sell Signal Triggered!")
        place_order('sell')
        entry_price = price_data['close'].iloc[-1]
        max_price_since_entry = entry_price  # Initial max price is entry price

    # Risk Management: Check trailing stop and take-profit condition
    if last_order == 'buy':
        check_trailing_stop_or_take_profit(price_data['close'].iloc[-1])
    elif last_order == 'sell':
        check_trailing_stop_or_take_profit(price_data['close'].iloc[-1])

    if backtest:
        backtest_results.append({
            'timestamp': price_data['timestamp'].iloc[-1],
            'price': price_data['close'].iloc[-1],
            'position': last_order,
            'balance': account_balance,
            'entry_price': entry_price,
            'position_size': position_size
        })

# Function to check trading signal based on moving average crossover, RSI, and MACD
def check_signal(df):
    if len(df) < long_window:
        return None  # Wait until enough data is received

    # Calculate moving averages
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()

    # Calculate RSI
    df['rsi'] = pdta.rsi(df['close'], length=rsi_period)

    # Calculate MACD and Signal Line
    macd = pdta.macd(df['close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    df['macd'] = macd['MACD']
    df['macd_signal'] = macd['MACDs']

    # Strategy: Moving Average Crossover with RSI and MACD confirmation
    if df['short_ma'].iloc[-2] < df['long_ma'].iloc[-2] and df['short_ma'].iloc[-1] > df['long_ma'].iloc[-1] and df['rsi'].iloc[-1] < 70 and df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
        return 'buy'
    elif df['short_ma'].iloc[-2] > df['long_ma'].iloc[-2] and df['short_ma'].iloc[-1] < df['long_ma'].iloc[-1] and df['rsi'].iloc[-1] > 30 and df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]:
        return 'sell'
    return None  # No signal


# Function to place order (mockup for real order logic)
def place_order(action):
    global last_order
    if last_order == action:
        print(f"Already placed a {action} order. Skipping.")
        return

    # Send a mock order to CoinDCX
    print(f"Placing {action} order on CoinDCX...")
    # In real implementation, you would call the CoinDCX API here
    last_order = action


# Function to calculate position size based on risk management
def calculate_position_size():
    global account_balance
    risk_per_trade = 0.02  # Risk 2% per trade
    stop_loss_amount = account_balance * risk_per_trade  # Risked amount
    stop_loss_distance = stop_loss_percentage * account_balance  # Example distance for stop-loss calculation
    position_size = stop_loss_amount / stop_loss_distance  # Position size formula
    return position_size

# Function to check trailing stop or take-profit conditions
def check_trailing_stop_or_take_profit(current_price):
    global entry_price, max_price_since_entry, position_size

    # Calculate the trailing stop price
    trailing_stop_price = max_price_since_entry * (1 - trailing_stop_percentage)

    if last_order == 'buy':
        # Trigger trailing stop if price falls below trailing stop price
        if current_price <= trailing_stop_price:
            print("Trailing Stop Triggered!")
            place_order('sell')
    elif last_order == 'sell':
        # Trigger trailing stop if price rises above trailing stop price
        if current_price >= trailing_stop_price:
            print("Trailing Stop Triggered!")
            place_order('buy')

    # Check take-profit condition
    if (last_order == 'buy' and current_price >= entry_price * (1 + take_profit_percentage)) or \
       (last_order == 'sell' and current_price <= entry_price * (1 - take_profit_percentage)):
        print("Take-profit triggered!")
        place_order('sell' if last_order == 'buy' else 'buy')

# Function to convert the incoming message into a DataFrame
def convert_pd(data):
    candle_data = json.loads(data['data'])

    df = pd.DataFrame([{
        'timestamp': candle_data['t'],
        'open': float(candle_data['o']),
        'close': float(candle_data['c']),
        'high': float(candle_data['h']),
        'low': float(candle_data['l']),
        'volume': float(candle_data['v']),
        'quote_volume': float(candle_data['q']),
        'trades': candle_data['n']
    }])
    return df

def backtest_strategy():
    global backtest_results
    print("Backtesting started...")
    
    # Iterate over historical data and simulate trading
    for i, row in historical_data.iterrows():
        price_data = pd.DataFrame([row])
        on_message({'data': json.dumps(row.to_dict())})

    # Print backtest results
    print("Backtest results:")
    print(pd.DataFrame(backtest_results))



def main():
    if backtest:
        backtest_strategy()
    else:
        try:
            sio.connect(socketEndpoint, transports='websocket')
            while True:
                time.sleep(1)  # Keep the connection alive
        except Exception as e:
            print(f"Error connecting to the server: {e}")
            raise

# Run the main function
if __name__ == '__main__':
    main()

