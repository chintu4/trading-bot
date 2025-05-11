import time
import hashlib
import json
import requests
import pandas as pd
import hmac

secret_bytes=bytes(secret,encoding="utf-8")

SYMBOL='B-BTC_USDT'
INTERVAL='15m'
RSI_WINDOW=14
RSI_BUY_THRESHOLD=30
RSI_SELL_THRESHOLD=70
INVESTMENT_AMOUNT_INR=50
LEVERAGE=1
SLEEP_INTERVAL=60*5


def get_candlestick_data(symbol,interval):
    url=f'https://public.coindcx.com/market_data/candles?pair={symbol}&interval={interval}'
    response=requests.get(url)
    data=response.json()
    return data
def calculate_rsi(data,window):
    df=pd.DataFrame(data)
    df['close']=df['close'].astype(float)
    df=df[::-1]

def get_spot_ltp():
    url="https://api.coindcx.com/exchange/ticker"
    response=requests.get(url)
    data=response.json()
    df=pd.DataFrame(data)
    return df
def place_order(side,symbol,limit_price,quantity):
    time=int(round(time.time()*1000))
    body={
        "timestamp":time,
        "market":symbol,
        "order_type":side,
        "limit_price":limit_price,
        "quantity":quantity,# total_quantity
        "leverage":LEVERAGE,
    }
    json_body=json.dumps(body,separators=(',',':'))
    signature=hmac.new(secret_bytes,json_body.encode(),hashlib.sha256).hexdigest()
    url=f"https://api.coindcx.com/exchange/v1/orders/create"
    headers={
        "Content-Type":"application/json",
        "X-AUTH-APIKEY":api_key,
        "X-AUTH-SIGNATURE":signature
    }
    response=requests.post(url,data=json_body,headers=headers)
    return response.json()
    


def calculate_quantity(investment_account,current_price):
    return round(investment_account/current_price)


def run_rsi_bot():
    while True:
        try:
            data=get_candlestick_data(symbol,interval)
            df=calculate_quantity(data,rsi_window)
            latest_data=df.iloc[-1]
            latest_close=latest_data['close']
            latest_rsi=latest_data['rsi']
            if latest_rsi<latest_rsi:
                quantity=calculate_quantity(investment_account=investment_account,latest_close)
                order_response=place_order("buy",symbol,latest_close,quantity)
                print(f"place buy order: {order_response}")
            elif latest_rsi>rsi_sell_threshold:
                quantity=calculate_quantity(investment_account=INVESTMENT_AMOUNT,latest_close)
                order_response=place_order("sell",symbol,latest_close,quantity)
                print(f"Placed sell order:{order_response}")
        except Exception as e:
            print(f"Error occurred:{e}")
        time.sleep(SLEEP_INTERVAL)


def arbitage_opportunity():
    spot_df=get_spot_ltp()
    btc_inr=float(spot_df[spot_df['market']=='BTCINR']['last_price'].values.tolist()[0])
    btc_usdt=float(spot_df[spot_df['market']=='BTCINR']['last_price'].values.tolist()[0])
    usdt_inr=float(spot_df[spot_df['market']=='BTCINR']['last_price'].values.tolist()[0])

    btc_calculated_value=float(btc_usdt)*float(usdt_inr)

    print(f"BTC/INR : {btc_inr} ,BTC/USDT :{ btc_usdt},USDT/INR :{usdt_inr} ,Calculated BTC/INR {btc_cal}")

    sell_response=place_order('sell',"BTCINR",btc_inr),quantity_usdt

    print(f"sell BTC/INR Order Response : {sell_response}")

    if btc_calculated_value <btc_inr :
        print("BTC USDT values are lower than INR values- buying BTC/INR ")
        quantity_usdt=round(INVESTMENT_AMOUNT_INR/btc_inr)
        buy_response=place_order("buy","BTCUSDT",btc_usdt)
        print(f"Buy BTC/USDT Order Response :{buy_response}")
        buy_response=place_order("buy","BTCUSDT",btc_usdt)
    elif btc_calculated_value>btc_inr:
        print("BTC USDT values are higher than INR values -Buying BTC/INR and selling BTC/USDT")
        quantity_inr=round(INVESTMENT_AMOUNT_INR/btc_inr,3)
        buy_response=place_order('buy','BTCINR',btc_inr,quantity_inr)
        print(f"Buy BTC/INR Order Response :{buy_response}")

        sell_response=place_order("sell","BTCUSDT",btc_usdt,quantity_inr)
        print(f"Sell BTC/USDT Order REsponse :{sell_response}")
    else:
        print("No arbitage opportunity")

    
def run_arbitage_bot():
    while True:
        try:
            arbitage_opportunity()
        except Exception as e:
            print(f"Error occurred:{e}")
        time.sleep(SLEEP_INTERVAL)




