class PercentageStrategy:
    def __init__(self, exchange_api):
        self.exchange_api = exchange_api

    def calculate_percentage_change(self, old_price, new_price):
        return ((new_price - old_price) / old_price) * 100

    def execute(self, symbol, trade_quantity, buy_threshold, sell_threshold):
        try:
            current_price = self.exchange_api.get_latest_price(symbol)
        except Exception as e:
            print(f"Error fetching the latest price for {symbol}: {e}")
            return
        market_data = self.exchange_api.get_market_data()
        
        # Get the last price from market data (this could be more complex depending on API)
        last_price = float(market_data['data'][symbol]['last_price'])

        # Calculate the percentage change
        percentage_change = self.calculate_percentage_change(last_price, current_price)
        
        if percentage_change >= buy_threshold:
            print(f"Buy signal for {symbol}, price increased by {percentage_change}%")
            # Place Buy order logic here
            self.exchange_api.place_order(symbol, trade_quantity, current_price, 'buy', 'limit_order')

        elif percentage_change <= -sell_threshold:
            print(f"Sell signal for {symbol}, price decreased by {percentage_change}%")
            # Place Sell order logic here
            self.exchange_api.place_order(symbol, trade_quantity, current_price, 'sell', 'limit_order')
