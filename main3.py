import requests
import plotly.graph_objects as go
import pandas as pd
def get_Candle():
    url = "https://public.coindcx.com/market_data/candlesticks"
    
    def get_epoch_time(year, month, day, hour, minute, second):
        """
        Returns the epoch time in seconds for a given date and time in local time.
        """
        return int(pd.Timestamp(year=year, month=month, day=day, hour=hour, minute=minute, second=second).timestamp())
    # import 
    query_params = {
        "pair": "B-MKR_USDT",
        "from": get_epoch_time(2025, 1, 31, 0, 0, 0),
        "to": get_epoch_time(2025, 2, 2, 0, 0, 0),
        "resolution": "60m",  # '1' OR '5' OR '60' OR '1D'
        "pcode": "f"
    }
    response = requests.get(url, params=query_params)
    if response.status_code == 200:
        data = response.json()
        # Process the data as needed
        print(data)
    else:
        print(f"Error: {response.status_code}, {response.text}")
    
    
    if response.status_code == 200:
        df = pd.DataFrame(data['data'], columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        fig = go.Figure(data=[go.Candlestick(x=df['time'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])
        fig.show()
