import time
import pandas as pd

"""
I need to store the last traded price in a csv file
"""
# pd.file_size()
# pd.read_csv()
# pd.to_csv()

class PercentageStrategy:
    def __init__(self, exchange_api,fileName):
        self.exchange_api = exchange_api
        self.profitPercentage=0.05
        self.stopLoss=0.02
        self.fileName=fileName

    def calculate_percentage_change(self, old_price, new_price):
        return ((new_price - old_price) / old_price) * 100
    
    def get_current_price(self, symbol):
        return self.exchange_api.get_current_price(symbol)
    
    def execute(self, symbol, trade_quantity, buy_threshold, sell_threshold):
        try:
            current_price = self.exchange_api.get_current_price(symbol)
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
    def is_buy(self,current_price):
        last_price=pd.read_csv(self.fileName)
        if self.calculate_percentage_change(current_price,)> self.profitPercentage:
            return True
        else:
            return False
            # pass
            
        # pass
    def is_sell(self,currentPrice):
        last_price=pd.read_csv(self.fileName)

        if self.calculate_percentage_change(currentPrice,last_price)<self.stopLoss:
            return True
        else:
            return False
            # pass

        # pass
    def profit_price(self,current_price):
        return current_price + (current_price*self.profitPercentage)
    
    def loss_price(self,current_price):
        return current_price-(current_price*self.stopLoss)
        
