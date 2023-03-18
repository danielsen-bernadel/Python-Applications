from CS import *


utc_tz = pytz.timezone('UTC')
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display

if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()
mt5.login(41694719)

time_frame=[mt5.TIMEFRAME_M1,mt5.TIMEFRAME_M5,mt5.TIMEFRAME_M15]

#Set parameters for time
timezone = pytz.timezone("UTC")
now = datetime.now(timezone)
start = datetime.now(timezone) - dt.timedelta(days=5)
utc_from = datetime(start.year, start.month, start.day)
utc_to = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
#Pull price data from MT5
rates = mt5.copy_rates_range(Symbol, mt5.TIMEFRAME_M15, utc_from, utc_to)
#Format Data in Pandas DataFrames to be manipulated
htf = pd.DataFrame(rates)
htf['time']=pd.to_datetime(htf['time'], unit='s')

for i in range(2,htf.shape[0]):
    current = htf.iloc[i,:]
    prev = htf.iloc[i-1,:]
    prev_2 = htf.iloc[i-2,:]
    prev_3 = htf.iloc[i-3,:]
    prev_4 = htf.iloc[i-4,:]
    realbody = abs(current['open'] - current['close'])
    candle_range = current['high'] - current['low']
    idx = htf.index[i]
    htf.loc[idx,'Bullish swing'] = current['low'] > prev['low'] > prev_2['low'] < prev_3['low'] < prev_4['low']
    htf.loc[idx,'Bearish swing'] = current['high'] < prev['high'] < prev_2['high'] > prev_3['high'] > prev_4['high']
    #Finding the Bullish Market Shift
    if MS == 'Bullish':
        if htf.loc[idx,'Bullish swing'] == True:
            htf.loc[idx,'Bull1'] = htf['low'].loc[htf.index[i-2]]
            Bull1= htf.loc[htf.index[i-2]]
        if htf.loc[idx,'Bearish swing'] == True and Bull1['time'] < htf.loc[idx,'time']:
            htf.loc[idx,'Bull2'] = htf['high'].loc[htf.index[i-2]]
            Bull2= htf.loc[htf.index[i-2]]
        if htf.loc[idx,'Bullish swing'] == True and Bull2['time'] < htf.loc[idx,'time']:
            htf.loc[idx,'Bull3'] = htf['low'].loc[htf.index[i-2]]
            Bull3= htf.loc[htf.index[i-2]]
    #Finding the Bearish Market Shift
    elif MS == 'Bearish':
        if htf.loc[idx,'Bearish swing'] == True:
            Bear1= htf['high'].loc[htf.index[i-2]]
            htf.loc[idx,'Bear1'] = htf['high'].loc[htf.index[i-2]]
        if htf.loc[idx,'Bullish swing'] == True and Bear1['time'] < htf.loc[idx,'time']:
            Bear2= htf['low'].loc[htf.index[i-2]]
            htf.loc[idx,'Bear2'] = htf['low'].loc[htf.index[i-2]]
        if htf.loc[idx,'Bearish swing'] == True and Bear2['time'] < htf.loc[idx,'time']:
            Bear3= htf['high'].loc[htf.index[i-2]]
            htf.loc[idx,'Bear3'] = htf['high'].loc[htf.index[i-2]]
if MS == 'Bullish':
    z = htf['Bull3'].last_valid_index()
    low = htf['Bull3'].loc[htf.index[z]]
    q = htf['Bull2'].tail(15).dropna()
    f = q.iloc[-2:]
    high = round(f.iloc[-2],5)
    print ('Price Entry Zone is from', low, 'to', high)
else:
    z = htf['Bear3'].last_valid_index()
    low = htf['Bear3'].loc[htf.index[z]]
    q = htf['Bear2'].tail(15).dropna()  
    f = q.iloc[-2:]
    high = round(f.iloc[-2],5)
    print ('Price Entry Zone is from', low, 'to', high)
    #print (htf.tail(15))
