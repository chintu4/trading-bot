import time
import pandas as pd
from services.cosmosdb_service import get_trade_history_container, create_item
from utils.logger import logger # Assuming logger is correctly set up in utils
from datetime import datetime, timezone
import uuid
from services.telegram_notifier import send_trade_notification

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
                if current_price is None: # Explicitly check if price is None
                    logger.error(f"{self.strategy_name}: Could not fetch current price for {symbol}. Aborting trade execution.")
                    return
                current_price = float(current_price) # Ensure it's a float
            except Exception as e:
                logger.error(f"{self.strategy_name}: Error fetching the latest price for {symbol}: {e}")
                return

            market_data = self.exchange_api.get_market_data()
            if not market_data or 'data' not in market_data or not isinstance(market_data['data'], dict) or symbol not in market_data['data'] or 'last_price' not in market_data['data'][symbol]:
                logger.error(f"{self.strategy_name}: Could not retrieve valid last_price for {symbol} from market_data. Structure may have changed or symbol data missing.")
                # Attempt to use current_price as last_price if market_data is faulty but current_price was fetched
                # This is a fallback, ideal solution is to ensure get_market_data() is robust or handle its errors better.
                # For now, let's be cautious and potentially skip if last_price is critical and missing.
                # Or, if current_price is reliable enough to be a proxy for last_price for percentage calculation in some scenarios.
                # Given the logic, percentage_change needs a distinct 'last_price'. So, if it's missing, we should probably return.
                logger.warning(f"{self.strategy_name}: Using current_price ({current_price}) as last_price due to market_data issues. This might not be accurate for change calculation if prices are volatile.")
                # If we decide this isn't acceptable:
                # logger.error(f"{self.strategy_name}: Critical market_data['data']['{symbol}']['last_price'] missing. Aborting.")
                # return
                # For now, proceeding with caution if current_price is available as a proxy for last_price
                last_price = current_price # Fallback, acknowledge potential inaccuracy
            else:
                try:
                    last_price = float(market_data['data'][symbol]['last_price'])
                except ValueError:
                    logger.error(f"{self.strategy_name}: Could not convert last_price '{market_data['data'][symbol]['last_price']}' to float for {symbol}. Aborting.")
                    return


            percentage_change = self.calculate_percentage_change(last_price, current_price)

            trade_attempted = False
            trade_type = None
            executed_price = current_price
            threshold_met = None
            exchange_order_id = None # To store the ID from the exchange

            if percentage_change >= buy_threshold:
                logger.info(f"{self.strategy_name}: Buy signal for {symbol}, price increased by {percentage_change:.2f}% (Threshold: {buy_threshold}%)")
                trade_attempted = True
                trade_type = "buy"
                threshold_met = buy_threshold
                logger.info(f"{self.strategy_name}: Attempting to place BUY order for {trade_quantity} of {symbol} at {executed_price}")
                try:
                    # Ensure exchange_api object has place_spot_order_now method
                    if hasattr(self.exchange_api, 'place_spot_order_now'):
                        exchange_order_id = self.exchange_api.place_spot_order_now(
                            symbol=symbol,
                            quantity=trade_quantity,
                            price=executed_price,
                            order_side='buy',
                            order_type='limit_order' # Assuming limit order as per previous logic
                        )
                        if exchange_order_id:
                            logger.info(f"{self.strategy_name}: BUY order placement initiated with Order ID: {exchange_order_id} for {symbol}.")
                        else:
                            logger.error(f"{self.strategy_name}: BUY order placement failed for {symbol}. No Order ID returned.")
                    else:
                        logger.error(f"{self.strategy_name}: Exchange API object does not have method 'place_spot_order_now'. Cannot place BUY order.")
                except Exception as e:
                    logger.error(f"{self.strategy_name}: Exception during BUY order placement for {symbol}: {e}", exc_info=True)
                    exchange_order_id = None # Ensure it's None on exception

            elif percentage_change <= -sell_threshold:
                logger.info(f"{self.strategy_name}: Sell signal for {symbol}, price decreased by {percentage_change:.2f}% (Threshold: -{sell_threshold}%)")
                trade_attempted = True
                trade_type = "sell"
                threshold_met = -sell_threshold
                logger.info(f"{self.strategy_name}: Attempting to place SELL order for {trade_quantity} of {symbol} at {executed_price}")
                try:
                     # Ensure exchange_api object has place_spot_order_now method
                    if hasattr(self.exchange_api, 'place_spot_order_now'):
                        exchange_order_id = self.exchange_api.place_spot_order_now(
                            symbol=symbol,
                            quantity=trade_quantity,
                            price=executed_price,
                            order_side='sell',
                            order_type='limit_order' # Assuming limit order
                        )
                        if exchange_order_id:
                            logger.info(f"{self.strategy_name}: SELL order placement initiated with Order ID: {exchange_order_id} for {symbol}.")
                        else:
                            logger.error(f"{self.strategy_name}: SELL order placement failed for {symbol}. No Order ID returned.")
                    else:
                        logger.error(f"{self.strategy_name}: Exchange API object does not have method 'place_spot_order_now'. Cannot place SELL order.")
                except Exception as e:
                    logger.error(f"{self.strategy_name}: Exception during SELL order placement for {symbol}: {e}", exc_info=True)
                    exchange_order_id = None # Ensure it's None on exception

            # The rest of the method (Cosmos DB logging) will be updated in the next plan step
            # For now, this step focuses on making the call and getting the order_id.
            # The 'trade_executed' flag for Cosmos logging should be based on 'exchange_order_id is not None'.
            trade_successfully_placed = exchange_order_id is not None

            if trade_attempted and self.trade_history_container:
                # Determine the status at placement
                if trade_successfully_placed:
                    current_order_status_at_placement = "SUBMITTED_TO_EXCHANGE"
                else:
                    current_order_status_at_placement = "PLACEMENT_FAILED"

                trade_document = {
                    "id": str(uuid.uuid4()),  # Unique ID for the document, also partition key
                    "strategy_name": self.strategy_name,
                    "symbol": symbol,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(), # Time of signal/placement attempt
                    "trade_type": trade_type, # 'buy' or 'sell'
                    "price_intended": executed_price,
                    "quantity_intended": trade_quantity,
                    "percentage_change_trigger": round(percentage_change, 4),
                    "threshold_met": threshold_met,
                    "exchange_order_id": exchange_order_id if exchange_order_id else "N/A",
                    "order_status_at_placement": current_order_status_at_placement
                    # Consider adding a field for error details if placement_failed, though general errors are logged
                    # "placement_error_details": "Error message if any"
                }
                try:
                    if trade_type: # Only log if a buy/sell decision was made (trade_type is set)
                        create_item(self.trade_history_container, trade_document)
                        logger.info(f"{self.strategy_name}: Trade signal for {symbol} (Order ID: {trade_document['exchange_order_id']}) logged to Cosmos DB with status: {trade_document['order_status_at_placement']}.")
                except Exception as e:
                    logger.error(f"{self.strategy_name}: Failed to log trade signal for {symbol} (Order ID: {trade_document['exchange_order_id']}) to Cosmos DB: {e}", exc_info=True)
            elif trade_attempted and not self.trade_history_container:
                logger.warning(f"{self.strategy_name}: Trade signal occurred for {symbol} but Cosmos DB container is not available. Signal not logged.")

            # --- Add Telegram Notification Logic ---
            if trade_attempted and trade_type: # Ensure a decision was made and trade_type is set
                message_lines = [
                    f"*Trade Signal: {self.strategy_name}*",
                    f"Symbol: `{symbol}`",
                    f"Type: `{trade_type.upper()}`",
                    f"Intended Price: `{executed_price}`",
                    f"Intended Quantity: `{trade_quantity}`"
                ]

                if trade_successfully_placed and exchange_order_id: # trade_successfully_placed was set earlier
                    message_lines.append(f"Status: `SUBMITTED_TO_EXCHANGE`")
                    message_lines.append(f"Exchange Order ID: `{exchange_order_id}`")
                else:
                    message_lines.append(f"Status: `PLACEMENT_FAILED`")
                    if exchange_order_id: # Should be rare if !trade_successfully_placed, but good for completeness
                         message_lines.append(f"Exchange Order ID (if any): `{exchange_order_id}`")

                # Add percentage change and threshold
                message_lines.append(f"Trigger: Change {percentage_change:.2f}% (Threshold: {threshold_met}%)")

                telegram_message = "\n".join(message_lines)

                try:
                    logger.info(f"{self.strategy_name}: Attempting to send Telegram notification for {symbol}...")
                    success = send_trade_notification(telegram_message)
                    if success:
                        logger.info(f"{self.strategy_name}: Telegram notification sent for {symbol}.")
                    else:
                        logger.warning(f"{self.strategy_name}: Telegram notification failed to send for {symbol}.")
                except Exception as e:
                    logger.error(f"{self.strategy_name}: Exception while trying to send Telegram notification for {symbol}: {e}", exc_info=True)
            # --- End of Telegram Notification Logic ---

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
        
