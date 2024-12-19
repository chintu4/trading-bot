class ExchangeAPI:
    def get_market_data(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def get_latest_price(self, symbol):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def place_order(self, symbol, quantity, price, order_side, order_type):
        raise NotImplementedError("This method should be overridden by subclasses.")
