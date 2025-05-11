import socketio
import pandas as pd
import pandas_ta as pdta
socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.Client()
import helper as hp

import json

futurePair=["B-ID_USDT@prices-futures"]
sportPair=["B-BTC_USDT_1m","B-BTC_USDT_1m"]
instrument=sportPair[0]

@sio.event
def connect():
    print("I'm connected!")
    sio.emit('join', {'channelName': instrument})

@sio.on('candlestick')
def on_message(response):
    print("candlestick Response !!!")
    # hp.save_data("BTC.csv",convert_pd(response))
    df=convert_pd(response)
    df = pd.concat([df, ], ignore_index=True)
    # convert_pd()
    # df=pd.DataFrame(response)
    print(df.tail())
    
    # print(response)
#how should trading sygnal be triggered
#


# Sample data from the API response


def convert_pd(data):
    # Parse the JSON string inside 'data' key
    candle_data = json.loads(data['data'])

    # Create a DataFrame
    df = pd.DataFrame([{
        'timestamp': candle_data['t'],
        'open': float(candle_data['o']),
        'close': float(candle_data['c']),
        'high': float(candle_data['h']),
        'low': float(candle_data['l']),
        'volume': float(candle_data['v']),
        'quote_volume': float(candle_data['q']),
        'trades': candle_data['n']
    }])
    return df

    print(df)

def main():
    try:
        sio.connect(socketEndpoint, transports='websocket')
        while True:
            sio.event('candlestick', {'channelName': instrument})
    except Exception as e:
        print(f"Error connecting to the server: {e}")
    raise
# Run the main function
if __name__ == '__main__':
    main()
