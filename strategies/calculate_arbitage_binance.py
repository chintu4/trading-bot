import requests
import pandas as pd

# Binance API endpoints
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/bookTicker"

def get_binance_prices():
    """Fetch the latest market price data from Binance API and return a DataFrame."""
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        df = pd.DataFrame(data)
        df.to_json('binance_ticker.json', orient='records')
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Binance: {e}")
        return None

def calculate_binance_arbitrage(df):
    """Calculate arbitrage between INR -> USDT -> BTC -> INR and INR -> BTC -> USDT -> INR."""
    
    if df is None:
        print("No data to calculate arbitrage.")
        return

    # Extract prices for relevant trading pairs
    try:
        # Binance does not support INR directly, so we assume USDTINR rate from another source
        # For example, you can fetch USDTINR rate from CoinDCX or another exchange
        usdt_inr_rate = 82.5  # Example: 1 USDT = 82.5 INR (fetch this dynamically from another API)

        # Fetch BTCUSDT prices from Binance
        btc_usdt_data = df[df['symbol'] == 'BTCUSDT']
        btc_usdt_ask = float(btc_usdt_data['askPrice'].values[0])
        btc_usdt_bid = float(btc_usdt_data['bidPrice'].values[0])
    except (IndexError, KeyError) as e:
        print(f"Error fetching market data: {e}")
        return

    # Binance fees (0.1% taker fee by default)
    taker_fee = 0.001  # 0.1%

    # Function to calculate final amount after fees
    def calculate_final_amount(amount, price, fee):
        return (amount / price) * (1 - fee)

    # Arbitrage Path 1: INR -> USDT -> BTC -> INR
    initial_inr = 1000  # Example starting capital in INR

    # Step 1: INR -> USDT
    usdt_bought = calculate_final_amount(initial_inr, usdt_inr_rate, taker_fee)
    # Step 2: USDT -> BTC
    btc_bought = calculate_final_amount(usdt_bought, btc_usdt_ask, taker_fee)
    # Step 3: BTC -> INR (using USDTINR rate)
    final_inr = (btc_bought * btc_usdt_bid) * usdt_inr_rate * (1 - taker_fee)

    profit1 = final_inr - initial_inr

    # Arbitrage Path 2: INR -> BTC -> USDT -> INR
    # Step 1: INR -> BTC (using USDTINR rate)
    btc_bought2 = calculate_final_amount(initial_inr / usdt_inr_rate, btc_usdt_ask, taker_fee)
    # Step 2: BTC -> USDT
    usdt_received = calculate_final_amount(btc_bought2 * btc_usdt_bid, 1, taker_fee)
    # Step 3: USDT -> INR
    final_inr2 = usdt_received * usdt_inr_rate * (1 - taker_fee)

    profit2 = final_inr2 - initial_inr

    print(f"Path 1 (INR -> USDT -> BTC -> INR) Profit: ₹{profit1:.2f}")
    print(f"Path 2 (INR -> BTC -> USDT -> INR) Profit: ₹{profit2:.2f}")

    if profit1 > 0:
        print("Arbitrage Opportunity Exists in Path 1!")
    if profit2 > 0:
        print("Arbitrage Opportunity Exists in Path 2!")

# Execute the script
df = get_binance_prices()
calculate_binance_arbitrage(df)