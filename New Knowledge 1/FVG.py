from MS import *

#This will need to be updated to take in the date and time from previous script
if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()
mt5.login(41694719)

timezone = pytz.timezone("UTC")
now = datetime.now(timezone)
start = datetime.now(timezone) - dt.timedelta(days=5)
utc_from = datetime(start.year, start.month, start.day)
utc_to = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
rates = mt5.copy_rates_range(Symbol, mt5.TIMEFRAME_M5, utc_from, utc_to)
htf = pd.DataFrame(rates)
htf['time']=pd.to_datetime(htf['time'], unit='s')
start=time.time()

for i in range(2,htf.shape[0]):
    current = htf.iloc[i,:]
    prev = htf.iloc[i-1,:]
    prev_2 = htf.iloc[i-2,:]
    prev_3 = htf.iloc[i-3,:]
    realbody = abs(current['open'] - current['close'])
    candle_range = current['high'] - current['low']
    idx = htf.index[i]
    htf.loc[idx,'Bullish FVG'] = current['low'] > prev_2['high'] and current['high'] > prev['high'] and prev['high'] > prev_2['high']
    htf.loc[idx,'Bearish FVG'] = current['high'] < prev_2['low'] and current['low'] < prev['low'] and prev['low'] < prev_2['low']
    if htf.loc[idx,'Bullish FVG'] == True:
        htf.loc[idx,'PEP'] = htf.loc[idx, 'low']
        if high > htf.loc[idx, 'PEP'] > low:
            Bull_PEP= htf.loc[idx, 'low']
            Bull_SL=htf.loc[idx-2, 'low']
            PEP_time=htf.loc[idx, 'time']
    elif htf.loc[idx,'Bearish FVG'] == True:
        htf.loc[idx,'PEP'] = htf.loc[idx, 'high']
        if high > htf.loc[idx, 'PEP'] > low:
            Bear_PEP = htf.loc[idx, 'high']
            Bear_SL=htf.loc[idx-2, 'high']
            PEP2_time=htf.loc[idx, 'time']
if MS == 'Bullish':
    #print (PEP_time)
    #print (htf.tail(15))
    a = (round(Bull_PEP,4))
    b = (round(Bull_SL,5))
    c = a + (2*(abs(b-a)))
    print ('PEP is:',a,' at:',PEP_time,' SL is:',round(b,4), ' TP is:',round(c,4))
    print (high > a > low)
elif MS == 'Bearish':
    #print (PEP2_time)
    #print (htf.tail(15))
    a = (round(Bear_PEP,4)) 
    b = (round(Bear_SL,5))
    c = a - (2*(b-a))
    print ('PEP is:',a,' at:',PEP2_time,' SL is:',round(b,4), ' TP is:',round(c,4))
    print (high > a > low)
else:
    print ("Hold your horses. Come back in an hour.")