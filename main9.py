import socketio
import pandas as pd
import pandas_ta as pdta
import json
import time
import os

csv_file = "./data/B_BTC_USDT_1m.csv"
# WebSocket Endpoint
socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.Client()
instrument = "B-BTC_USDT_1m"  # Ensure this is a valid trading pair

# Moving Average Crossover Strategy Parameters
short_window = 9
long_window = 10  # Reduced
rsi_period = 14
macd_fast = 5    # Reduced
macd_slow = 10   # Reduced
macd_signal = 3  

# DataFrame to store price data
if os.path.exists(csv_file):
    price_data = pd.read_csv(csv_file)
else:
    price_data = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Connection Event
@sio.event
def connect():
    print("✅ Connected to WebSocket!")
    sio.emit('join', {'channelName': instrument})
    print(f"📡 Subscribed to: {instrument}")

# Debugging: Print all received events
@sio.on('*')
def catch_all(event, data):
    print(f"📩 Event Received: {event}, Data: {data}")

# Handle Candlestick Data
@sio.on('candlestick')  # Confirm correct event name from CoinDCX API
def on_message(response):
    global price_data

    # Convert response to DataFrame
    df = convert_pd(response)

    if df is not None and not df.empty:
        price_data = pd.concat([price_data, df], ignore_index=True)

        # Keep only the last `long_window` candles
        if len(price_data) > long_window:
            price_data = price_data.tail(long_window)

        price_data.to_csv(csv_file, index=False)

        print(f"🕯 Latest Candle: {df.to_dict(orient='records')}")
        
        # Check for buy/sell signal
        signal = check_signal(price_data)
        if signal:
            print(f"🚀 Trading Signal: {signal.upper()}")



# Function to determine trading signal
def check_signal(df):
    if len(df) < macd_slow:
        print("⚠️ Not enough data for MACD calculation")
        return None  # Not enough data

    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    df['rsi'] = pdta.rsi(df['close'], length=rsi_period)
    df.fillna(method='34', inplace=True)
    
    macd = pdta.macd(df['close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    
    if macd is None or macd.isnull().values.any():
        print("⚠️ MACD calculation failed or contains NaN values. Waiting for more data.")
        return None
    
    macd.fillna(method='ffill', inplace=True)  # Forward-fill missing values
    
    df['macd'] = macd['MACD']
    df['macd_signal'] = macd['MACDs']
    
    # Buy Condition: Short MA crosses above Long MA, RSI < 70, MACD > MACD Signal
    if (
        df['short_ma'].iloc[-2] < df['long_ma'].iloc[-2] and
        df['short_ma'].iloc[-1] > df['long_ma'].iloc[-1] and
        df['rsi'].iloc[-1] < 70 and
        df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]
    ):
        return 'buy'

    # Sell Condition: Short MA crosses below Long MA, RSI > 30, MACD < MACD Signal
    elif (
        df['short_ma'].iloc[-2] > df['long_ma'].iloc[-2] and
        df['short_ma'].iloc[-1] < df['long_ma'].iloc[-1] and
        df['rsi'].iloc[-1] > 30 and
        df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]
    ):
        return 'sell'

    return None  # No signal

def stg1():
    """
    
    """
    pass


# Function to convert WebSocket response to DataFrame
def convert_pd(data):
    try:
        candle_data = json.loads(data['data'])
        df = pd.DataFrame([{
            'timestamp': candle_data['t'],
            'open': float(candle_data.get('o', 0)),
            'close': float(candle_data.get('c', 0)),
            'high': float(candle_data.get('h', 0)),
            'low': float(candle_data.get('l', 0)),
            'volume': float(candle_data.get('v', 0))
        }])
        return df
    except (ValueError, KeyError, TypeError) as e:
        print(f"⚠️ Data Parsing Error: {e}")
        return None

# Main function
def main():
    try:
        sio.connect(socketEndpoint, transports=['websocket'])
        print("🔄 WebSocket Running...")
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"❌ WebSocket Error: {e}")

# Run
if __name__ == '__main__':
    main()
