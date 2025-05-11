import json
import time
import random  # Simulating price data, replace with API calls

# File to store the last buy price
DATA_FILE = "trading_data.json"


def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_buy_price": None}


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)


def get_current_price():
    """Simulate getting current asset price. Replace with actual API call."""
    return round(random.uniform(90, 110), 2)  # Simulating price changes


def should_buy(current_price, last_buy_price):
    if last_buy_price is None:  # Always allow buying after a reset
        return True
    if current_price is None:
        return False
    if current_price >= (last_buy_price * 0.95):
        return False
    
    return current_price > last_buy_price  # Continue buying on upward trend



def should_sell(current_price, last_buy_price):
    if last_buy_price is None or current_price is None:
        return False
    # Simulate a sell signal
    if current_price < (last_buy_price):
        return True
    
    return last_buy_price is not None and current_price >= last_buy_price * 1.05


def main():
    data = load_data()
    last_buy_price = data["last_buy_price"]
    
    current_price = get_current_price()
    print(f"Current Price: {current_price}")
    
    if should_buy(current_price, last_buy_price):
        print(f"Buying at {current_price}")
        data["last_buy_price"] = current_price
        save_data(data)
    elif should_sell(current_price, last_buy_price):
        print(f"Selling at {current_price}, Profit: {current_price - last_buy_price}")
        data["last_buy_price"] = current_price  # Store last sell price instead of None
        save_data(data)

    else:
        print("No action taken.")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(5)  # Simulate waiting for market updates
