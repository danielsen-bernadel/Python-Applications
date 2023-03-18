#Import Necessary Libraries
from pytz import timezone
import matplotlib.pyplot as plt
import pandas as pd
import time
import datetime as dt
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pytz
import talib
import numpy
import schedule

def get_order_history(date_from, date_to):
    res = mt5.history_deals_get(date_from, date_to)
    
    if(res is not None and res != ()):
        df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    return pd.DataFrame()

def calc_daily_lost_trades():
    now = datetime.now().astimezone(pytz.timezone('UTC'))
    now = datetime(now.year, now.month, now.day, hour=now.hour, minute=now.minute)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    res = get_order_history(midnight, now)

    if(res.empty):
        return 0
    else:
        lost_trade_count = 0
        for i, row in res.iterrows():
            profit = float(row['profit'])
            if(profit < 0):
                lost_trade_count = lost_trade_count + 1
        return lost_trade_count

def get_account_info():
    res = mt5.account_info()
    return res

def get_daily_trade_data():
    now = datetime.now().astimezone(pytz.timezone('UTC'))
    now = datetime(now.year, now.month, now.day, hour=now.hour, minute=now.minute)
    yesterday = now - timedelta(hours=24)
    res = get_order_history(yesterday, now)
    #print(res)
    return res

get_daily_trade_data()