import ccxt
import pandas as pd
import pandas_ta as ta
import time
import os
from dotenv import load_dotenv
load_dotenv(".env")

# Initialize Binance API (Public Data)
# exchange = ccxt.binance()
exchange = ccxt.binance({
    'apiKey': os.getenv("BINANCE_API_KEY"),
    'secret': os.getenv("BINANCE_API_SECRET"),
    'options': {'defaultType': 'future'}
})
# Parameters
PAIR = "BTC/USDT"
TIMEFRAME = "5m"  # 5-minute candles
BALANCE = 10000  # Initial capital in USDT
POSITION_SIZE = 100  # Fixed trade size in USDT
ATR_MULTIPLIER = 1.5  # ATR-based stop-loss multiplier

# Track Positions & PnL
position = None  # {'side': 'long', 'entry_price': 40000, 'stop_loss': 39800}
profit_loss = 0  # Track PnL

def get_historical_data(pair, timeframe, limit=50):
    """Fetches live OHLCV historical data from Binance"""
    print("[INFO] Fetching historical data...")
    bars = exchange.fetch_ohlcv(pair, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def calculate_indicators(df):
    """Calculates RSI, MACD, ATR indicators"""
    print("[INFO] Calculating indicators...")
    df["rsi"] = ta.rsi(df["close"], length=14)
    df["macd"], df["macd_signal"], df["macd_hist"] = ta.macd(df["close"])
    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    return df

def check_signals(df):
    """Check for buy/sell signals using RSI & MACD"""
    print("[INFO] Checking signals...")
    last_row = df.iloc[-1]
    if last_row["rsi"] < 30 and last_row["macd"] > last_row["macd_signal"]:
        return "buy"
    elif last_row["rsi"] > 70 and last_row["macd"] < last_row["macd_signal"]:
        return "sell"
    return None

def calculate_stop_loss(entry_price, atr, side):
    """Calculates stop-loss based on ATR"""
    print("[INFO] Calculating stop-loss...")
    if side == "buy":
        return entry_price - (ATR_MULTIPLIER * atr)
    else:
        return entry_price + (ATR_MULTIPLIER * atr)

def execute_trade(side, price, atr):
    """Executes a virtual trade with a stop-loss"""
    global position, BALANCE
    if position:
        print("[WARNING] Trade rejected, position already open!")
        return
    
    stop_loss = calculate_stop_loss(price, atr, side)
    print(f"[TRADE] {side.upper()} @ {price:.2f}, Stop-Loss: {stop_loss:.2f}")
    position = {"side": side, "entry_price": price, "stop_loss": stop_loss}

def check_exit_conditions(price):
    """Checks if stop-loss is hit and exits trade"""
    global position, BALANCE, profit_loss
    if position:
        if (position["side"] == "buy" and price <= position["stop_loss"]) or \
           (position["side"] == "sell" and price >= position["stop_loss"]):
            
            # Calculate PnL
            trade_pnl = POSITION_SIZE * ((price - position["entry_price"]) if position["side"] == "buy" else 
                                         (position["entry_price"] - price))
            profit_loss += trade_pnl
            BALANCE += trade_pnl

            print(f"[EXIT] Stopped out @ {price:.2f}, PnL: {trade_pnl:.2f}, New Balance: {BALANCE:.2f}")
            position = None  # Close position

def trading_loop():
    """Main trading loop that runs continuously"""
    global position
    while True:
        df = get_historical_data(PAIR, TIMEFRAME)
        df = calculate_indicators(df)
        signal = check_signals(df)
        last_price = df.iloc[-1]["close"]

        if signal and not position:
            execute_trade(signal, last_price, df.iloc[-1]["atr"])

        check_exit_conditions(last_price)

        print(f"[INFO] Last Price: {last_price:.2f}, Current PnL: {profit_loss:.2f}")
        time.sleep(10)  # Wait before fetching new data

# Start trading bot
trading_loop()
