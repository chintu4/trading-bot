import time
import pandas as pd
from services.cosmosdb_service import get_trade_history_container, create_item
from utils.logger import logger # Assuming logger is correctly set up in utils
from datetime import datetime, timezone
import uuid

"""
I need to store the last traded price in a csv file
"""
# pd.file_size()
# pd.read_csv()
# pd.to_csv()

class PercentageStrategy:
    def __init__(self, exchange_api, fileName):
        self.exchange_api = exchange_api
        self.profitPercentage = 0.05
        self.stopLoss = 0.02
        self.fileName = fileName
        self.strategy_name = "PercentageStrategy" # Added for logging
        try:
            self.trade_history_container = get_trade_history_container()
            logger.info(f"{self.strategy_name}: Successfully connected to TradeHistory container.")
        except Exception as e:
            logger.error(f"{self.strategy_name}: Failed to connect to TradeHistory container: {e}")
            self.trade_history_container = None

    def calculate_percentage_change(self, old_price, new_price):
        return ((new_price - old_price) / old_price) * 100
    
    def get_current_price(self, symbol):
        return self.exchange_api.get_current_price(symbol)
    
    def execute(self, symbol, trade_quantity, buy_threshold, sell_threshold):
        try:
            current_price = self.exchange_api.get_current_price(symbol)
        except Exception as e:
            # Use logger instead of print
            logger.error(f"{self.strategy_name}: Error fetching the latest price for {symbol}: {e}")
            return
        
        # Assuming market_data structure is as expected.
        # Consider adding error handling for market_data access.
        market_data = self.exchange_api.get_market_data()
        if not market_data or 'data' not in market_data or symbol not in market_data['data'] or 'last_price' not in market_data['data'][symbol]:
            logger.error(f"{self.strategy_name}: Could not retrieve valid last_price for {symbol} from market_data.")
            return

        last_price = float(market_data['data'][symbol]['last_price'])
        percentage_change = self.calculate_percentage_change(last_price, current_price)
        
        trade_executed = False
        trade_type = None
        executed_price = current_price # Assuming order executes at current_price for this example
        threshold_met = None

        if percentage_change >= buy_threshold:
            logger.info(f"{self.strategy_name}: Buy signal for {symbol}, price increased by {percentage_change:.2f}% (Threshold: {buy_threshold}%)")
            # Placeholder: Actual order placement might return an order ID or confirmation
            # self.exchange_api.place_order(symbol, trade_quantity, current_price, 'buy', 'limit_order')
            logger.info(f"{self.strategy_name}: Executing BUY order for {trade_quantity} of {symbol} at {current_price}")
            # Simulate order placement for now for logging
            trade_executed = True
            trade_type = "buy"
            threshold_met = buy_threshold

        elif percentage_change <= -sell_threshold:
            logger.info(f"{self.strategy_name}: Sell signal for {symbol}, price decreased by {percentage_change:.2f}% (Threshold: -{sell_threshold}%)")
            # Placeholder: Actual order placement might return an order ID or confirmation
            # self.exchange_api.place_order(symbol, trade_quantity, current_price, 'sell', 'limit_order')
            logger.info(f"{self.strategy_name}: Executing SELL order for {trade_quantity} of {symbol} at {current_price}")
            # Simulate order placement for now for logging
            trade_executed = True
            trade_type = "sell"
            threshold_met = -sell_threshold

        if trade_executed and self.trade_history_container:
            trade_document = {
                "id": str(uuid.uuid4()),  # Unique ID for the trade document, also partition key
                "strategy_name": self.strategy_name,
                "symbol": symbol,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "trade_type": trade_type,
                "price": executed_price,
                "quantity": trade_quantity,
                "percentage_change_trigger": round(percentage_change, 4),
                "threshold_met": threshold_met,
                "order_status": "signal_placed_simulated", # Change if place_order returns actual status/ID
                # "exchange_order_id": "from_exchange_if_available"
            }
            try:
                create_item(self.trade_history_container, trade_document)
                logger.info(f"{self.strategy_name}: Successfully logged trade {trade_document['id']} for {symbol} to Cosmos DB.")
            except Exception as e:
                logger.error(f"{self.strategy_name}: Failed to log trade {trade_document.get('id')} for {symbol} to Cosmos DB: {e}")
        elif trade_executed and not self.trade_history_container:
            logger.warning(f"{self.strategy_name}: Trade executed for {symbol} but Cosmos DB container is not available. Trade not logged.")

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
        
