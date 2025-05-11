import requests
import pandas as pd

def get_price():
    """Fetch the latest market price data from CoinDCX API and return a DataFrame."""
    url = "https://api.coindcx.com/exchange/ticker"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        df = pd.DataFrame(data)
        df.to_json('ticker.json', orient='records')
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_arbitrage(df):
    """Calculate arbitrage between INR-USDT-BTC-INR and INR-BTC-USDT-INR."""
    
    if df is None:
        print("No data to calculate arbitrage.")
        return

    # Extract prices for relevant trading pairs
    try:
        usdt_inr_ask = df[df['market'] == 'USDTINR']['ask'].astype(float).values[0]
        usdt_inr_bid = df[df['market'] == 'USDTINR']['bid'].astype(float).values[0]
        btc_inr_ask = df[df['market'] == 'BTCINR']['ask'].astype(float).values[0]
        btc_inr_bid = df[df['market'] == 'BTCINR']['bid'].astype(float).values[0]
        btc_usdt_ask = df[df['market'] == 'BTCUSDT']['ask'].astype(float).values[0]
        btc_usdt_bid = df[df['market'] == 'BTCUSDT']['bid'].astype(float).values[0]
    except (IndexError, KeyError) as e:
        print(f"Error fetching market data: {e}")
        return

    # CoinDCX fees
    taker_fee = 0.0005  # 0.05%

    # Function to calculate final amount after fees
    def calculate_final_amount(amount, price, fee):
        return (amount / price) * (1 - fee)

    # Arbitrage Path 1: INR -> USDT -> BTC -> INR
    initial_inr = 500 #Example starting capital in INR

    usdt_bought = calculate_final_amount(initial_inr, usdt_inr_ask, taker_fee)
    btc_bought = calculate_final_amount(usdt_bought, btc_usdt_ask, taker_fee)
    final_inr = calculate_final_amount(btc_bought * btc_inr_bid, 1, taker_fee)

    profit1 = final_inr - initial_inr

    # Arbitrage Path 2: INR -> BTC -> USDT -> INR
    btc_bought2 = calculate_final_amount(initial_inr, btc_inr_ask, taker_fee)
    usdt_received = calculate_final_amount(btc_bought2 * btc_usdt_bid, 1, taker_fee)
    final_inr2 = calculate_final_amount(usdt_received * usdt_inr_bid, 1, taker_fee)

    profit2 = final_inr2 - initial_inr

    print(f"Path 1 (INR -> USDT -> BTC -> INR) Profit: ₹{profit1:.2f}")
    print(f"Path 2 (INR -> BTC -> USDT -> INR) Profit: ₹{profit2:.2f}")

    if profit1 > 0:
        print("Arbitrage Opportunity Exists in Path 1!")
    if profit2 > 0:
        print("Arbitrage Opportunity Exists in Path 2!")

# Execute the script
df = get_price()
calculate_arbitrage(df)