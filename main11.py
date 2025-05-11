import socketio
import pandas as pd
import pandas_ta as pdta
import json
import time
from strategies.percentage_strategy import PercentageStrategy
from services.coindcx_api import CoinDCXAPI

coindcx=CoinDCXAPI()
perSta=PercentageStrategy(coindcx,"C:/Users/dsjapnc/Documents/chintu Sharma/trading Pratform/data/PerSta.csv")
"""
implementing percentage stategy.
i need to save last traded data.
"""

# trasactionCSV="transaction.csv"
transactionJSON="transaction.json" # use it to save last traded price of particular coin


def extract_lastprice(pd):
    return pd["last_price"].iloc[0]



def main():
    # hmm=coindcx.get_market_data()
    data=pd.read_json('ticker.json')
    #suppose iam trasacting on price SOLINR
    #get sol current price 
    #store in csv or json
    sol_data=data[data['market']=='SOLINR']
    sol_data.to_json(transactionJSON)

    # current_price = sol_data['last_price'].iloc[0]
    current_price=extract_lastprice(sol_data)

    
    """
    last_price is buy price of coin
    make it dictionary ok
    """
    # current_price
    # print(current_price)
    # dicSave={'last_price':current_price}
    # with open(transactionJSON, "w") as my_file:
    #     my_file.write(str(dicSave))
    
    """ let suppose i made a buy transaction and saved the last traded price in trasactionJSON
    now wait untill the price reaches 5% more  and 2% loss,
    I need to also track the order
    if found errors then send an alert using telegram message
    """
    
    # print(yk['last_price'])
    
    #get last_price column and from last_price column 
    # hell=yk.to_csv('Transaction.csv')
    #just extract last_price
    # print(hell['symbol'])
    # ha=pd.Dataframe(hmm)
    #first buy
    # coindcx.place_spot_order_now()

    is_to_buy=True
    symbol="SOLINR"
    quantity= #quantity that i will get for a perticular price
    


    while True:

        #check for changes
        if perSta.is_sell(currentPrice=current_price) and is_to_buy==False:
            coindcx.place_spot_order_now(order_side="sell",symbol=symbol,order_type="limit_order",price=perSta.profit_price(current_price))
            # yk.to_csv(trasaction)

            is_to_buy=True
        if perSta.is_buy(current_price=current_price) and is_to_buy==True:
            is_to_buy=False
            coindcx.place_spot_order_now(order_side="buy",symbol=symbol,order_type="limit_order",price=perSta.loss_price(current_price=current_price))
            # yk.to_csv(trasaction)
    
        time.sleep(60)

main()