import krakenex
import pandas as pd
import pykrakenapi
import ta
from binance.client import Client
import mplfinance as mpl


### Create dataset
klinesT = Client().get_historical_klines('BTCEUR', Client.KLINE_INTERVAL_1HOUR, '01 November 2020')
df=pd.DataFrame(klinesT, columns= (['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']))

### Clean dataset
del df['Close time']
del df['Quote asset volume']
del df['Number of trades']
del df['Taker buy base asset volume']
del df['Taker buy quote asset volume']
del df['Ignore']

df['Open'] = pd.to_numeric(df['Open'])
df['High'] = pd.to_numeric(df['High'])
df['Low'] = pd.to_numeric(df['Low'])
df['Close'] = pd.to_numeric(df['Close'])

### Convert time
df = df.set_index(df['Open time'])
df.index=pd.to_datetime(df.index, unit='ms')

del df['Open time']

### Dataframe
print(df)

### Define indiators
MM_min=200
MM_max=600
df['SMA'+str(MM_min)] = ta.trend.sma_indicator(df['Close'], MM_min)
df['SMA'+str(MM_max)] = ta.trend.sma_indicator(df['Close'], MM_max)

### Backtest
fid = 113
btc = 0
fees=0.0026
lastIndex = df.first_valid_index()

for index, row in df.iterrows():
    if df['SMA'+str(MM_min)][lastIndex] > df['SMA'+str(MM_max)][lastIndex] and fid > 10:
        btc = fid / df['Close'][index] 
        btc = btc - fees * btc
        fid = 0
        print("Buy BTC at",df['Close'][index],'€ the', index)

    if df['SMA'+str(MM_min)][lastIndex] < df['SMA'+str(MM_max)][lastIndex] and btc > 0.0001:
        fid = btc * df['Close'][index]
        fid = fid - fees * fid
        btc = 0
        print("Sell BTC at",df['Close'][index],'€ the', index)
    lastIndex = index



### Results
finalResult = fid + btc * df['Close'].iloc[-1]
print("Final result",finalResult,'EUR')
print("Buy and hold result", (fid / df['Close'].iloc[0]) * df['Close'].iloc[-1],'EUR')

### Graph
df_graph=df.copy(deep=True)
del df_graph['SMA'+str(MM_min)]
del df_graph['SMA'+str(MM_max)]
del df_graph['Volume']

mpl.plot(df_graph, type='candle', mav=(MM_min,MM_max), warn_too_much_data=10000, style='yahoo')

'''
### Kraken
import krakenex
from pykrakenapi import *
api = krakenex.API()
k = KrakenAPI(api)

### Create dataset
ohlc, last = k.get_recent_trades('BTCUSD', since = '01 JAnuary 2021', ascending = True)
print(ohlc)

### Clean dataset
del ohlc['vwap']
del ohlc['count']

### Convert to numeric
ohlc['open']=pd.to_numeric(ohlc['open'])
ohlc['high']=pd.to_numeric(ohlc['high'])
ohlc['low']=pd.to_numeric(ohlc['low'])
ohlc['close']=pd.to_numeric(ohlc['close'])

### Convert time
ohlc = ohlc.set_index(ohlc['time'])

ohlc.index = pd.to_datetime(ohlc.index, unit='s')
del ohlc['time']

print(ohlc)'''
