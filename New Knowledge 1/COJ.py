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
import os
from slack import WebClient
import collections as coll
import tabulate
import talib as ta
from forex_python.converter import CurrencyRates

mt5.initialize()
mt5.login(62197811, password="gvfzkub7", server ="MetaQuotes-Demo")
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display

client = WebClient(token='xoxb-4029427242418-4026815945045-ggVYbyrwDcxzj6qoTprpLpdw')

def connect(account):
    account = int(account)
    mt5.initialize()
    authorized=mt5.login(62197811, password="gvfzkub7", server ="MetaQuotes-Demo")
    if authorized:
        print("Connected: Connecting to MT5 Client")
    else:
        print("Failed to connect at account #{}, error code: {}"
              .format(account, mt5.last_error()))

def daily_bal():
    mt5.initialize()
    authorized=mt5.login(62197811, password="gvfzkub7", server ="MetaQuotes-Demo")
    global daily
    daily = mt5.account_info()
    daily = daily.balance
    return daily

def get_pip_value(symbol : str) -> CurrencyRates:
    symbol_1 = symbol[0:3]
    symbol_2 = symbol[3:6]
    c = CurrencyRates()
    return c.convert(symbol_2, 'USD', c.convert(symbol_1, symbol_2, 1))
 
def calc_position_size(symbol : str, risk : float, sl : int) -> float:
    mt5.initialize()
    account = mt5.account_info()
    balance = float(account.balance)
    pip_value = get_pip_value(symbol)
    global lot_size
    lot_size = (balance * (risk / 100)) / (pip_value * sl)
    lot_size = round(lot_size, 2)
    return lot_size

def open_position(pair, order_type, lot_size, price, tp, sl):
    if order_type == 'Bullish':
        request = {"action": mt5.TRADE_ACTION_PENDING,
                    "symbol": pair,
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": price,
                    "sl": sl,
                    "tp": tp,
                    "deviation": 10,
                    "magic": 00000,
                    "comment": "insert comment",
                    "type_time": mt5.ORDER_TIME_GTC
                    }
    if order_type == 'Bearish':
        request = {"action": mt5.TRADE_ACTION_PENDING,
                    "symbol": pair,
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": price,
                    "sl": sl,
                    "tp": tp,
                    "deviation": 10,
                    "magic": 00000,
                    "comment": "insert comment",
                    "type_time": mt5.ORDER_TIME_GTC
                    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")
    else:
        print ("Order successfully placed!")
 
def positions_get():
    mt5.login(62197811, password="gvfzkub7", server ="MetaQuotes-Demo")
    res = mt5.positions_get()
    df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def close_position(deal_id):
    mt5.initialize()
    mt5.login(62197811, password="gvfzkub7", server ="MetaQuotes-Demo")
    print (deal_id)
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type  = open_positions.loc[open_positions['ticket'] == deal_id]['type'].values
    symbol = open_positions.loc[open_positions['ticket'] == deal_id]['symbol'].values
    volume = open_positions.loc[open_positions['ticket'] == deal_id]['volume'].values

    if(order_type == mt5.ORDER_TYPE_BUY_LIMIT):
        order_type = mt5.ORDER_TYPE_SELL
        try:
            price = open_positions.loc[open_positions['ticket'] == deal_id]['price_open'].values
        except:
            price = open_positions.loc[open_positions['ticket'] == deal_id]['price_current'].values   
    else:
        order_type = mt5.ORDER_TYPE_BUY
        try:
            price = open_positions.loc[open_positions['ticket'] == deal_id]['price_open'].values
        except:
            price = open_positions.loc[open_positions['ticket'] == deal_id]['price_current'].values 
	
    close_request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "position": deal_id,
        "price": price,
        "magic": 00000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
    }

    result = mt5.order_send(close_request)
    
    if mt5.TRADE_RETCODE_DONE:
        print ("Order successfully closed!")


def get_strength(time_frame):
    pairs = ["EURUSD","EURGBP","EURJPY","EURAUD","EURNZD",
    "EURCHF","EURCAD","GBPUSD", "GBPJPY","GBPAUD","GBPNZD","GBPCAD",
    "GBPCHF","USDCAD", "USDJPY","CHFJPY","CADJPY","NZDJPY","AUDJPY",
    "AUDNZD","AUDCAD", "NZDUSD","NZDCAD","NZDCHF","AUDCHF","CADCHF",
    "AUDUSD","USDCHF"]
    timezone = pytz.timezone("UTC")
    now = datetime.now(timezone)
    start = datetime.now(timezone) - dt.timedelta(days=7)
    utc_from = datetime(start.year, start.month, start.day)
    utc_to = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
    pair_data = dict()
    currency_strength = pd.DataFrame()
    rsi_df=pd.DataFrame()
    lastHourDateTime = datetime.now() - dt.timedelta(hours = 1)
    for pair in pairs:
        ohlc = mt5.copy_rates_from(pair, time_frame, lastHourDateTime, 15)
        df = pd.DataFrame(ohlc)
        rsi_df[pair]=talib.RSI(df.close,7)
    #Calculate Strength
    rsi_df.tail()
    strength=pd.DataFrame()
    strength["USD"]=1/7*((100-rsi_df.EURUSD)+(100-rsi_df.GBPUSD)+\
    rsi_df.USDCAD+rsi_df.USDJPY+(100-rsi_df.NZDUSD)+\
        (100-rsi_df.AUDUSD)+rsi_df.USDCHF)
    strength["EUR"]=1/7*(rsi_df.EURUSD+rsi_df.EURGBP+\
    rsi_df.EURJPY+rsi_df.EURAUD+rsi_df.EURNZD+rsi_df.EURCHF+\
        rsi_df.EURCAD)
    strength["GBP"]=1/7*(rsi_df.GBPUSD+rsi_df.GBPJPY+\
    rsi_df.GBPAUD+rsi_df.GBPNZD+rsi_df.GBPCAD+rsi_df.GBPCHF+\
        (100-rsi_df.EURGBP))
    strength["CHF"]=1/7*((100-rsi_df.EURCHF)+(100-rsi_df.GBPCHF)+\
    (100-rsi_df.NZDCHF)+(100-rsi_df.AUDCHF)+(100-rsi_df.CADCHF)+\
        rsi_df.CHFJPY+(100-rsi_df.USDCHF))
    strength["JPY"]=1/7*((100-rsi_df.EURJPY)+(100-rsi_df.GBPJPY)+\
    (100-rsi_df.USDJPY)+(100-rsi_df.CHFJPY)+(100-rsi_df.CADJPY)+\
        (100-rsi_df.NZDJPY)+(100-rsi_df.AUDJPY))
    strength["AUD"]=1/7*((100-rsi_df.EURAUD)+(100-rsi_df.GBPAUD)+\
    (100-rsi_df.AUDJPY)+rsi_df.AUDNZD+rsi_df.AUDCAD+
    rsi_df.AUDCHF+rsi_df.AUDUSD)
    strength["CAD"]=1/7*((100-rsi_df.EURCAD)+(100-rsi_df.GBPCAD)+\
    (100-rsi_df.USDCAD)+rsi_df.CADJPY+(100-rsi_df.AUDCAD)+\
        (100-rsi_df.NZDCAD)+rsi_df.CADCHF)
    strength["NZD"]=1/7*((100-rsi_df.EURNZD)+(100-rsi_df.GBPNZD)+\
    rsi_df.NZDJPY+rsi_df.NZDUSD+rsi_df.NZDCAD+rsi_df.NZDCHF+\
        (100-rsi_df.AUDNZD))
    #Determine Pairs ready for trading
    str =pd.DataFrame()
    str['Pair'] = ["USD","EUR","GBP","CHF","JPY","AUD","CAD","NZD"]
    str['CSscore'] = [int(strength['USD'].loc[strength.index[-1]]),int(strength['EUR'].loc[strength.index[-1]]),int(strength['GBP'].loc[strength.index[-1]]),int(strength['CHF'].loc[strength.index[-1]]),int(strength['JPY'].loc[strength.index[-1]]),int(strength['AUD'].loc[strength.index[-1]]),int(strength['CAD'].loc[strength.index[-1]]),int(strength['NZD'].loc[strength.index[-1]])]
    global ds
    ds = pd.DataFrame.from_dict({'Major_Pair' : ['EURUSD','GBPUSD','AUDUSD','NZDUSD','USDJPY','USDCHF','USDCAD'],
    'First Cur': ['EUR', 'GBP', 'AUD', 'NZD','USD','USD','USD'],
    '1st Value': [str['CSscore'].loc[str.index[1]], str['CSscore'].loc[str.index[2]], str['CSscore'].loc[str.index[5]], str['CSscore'].loc[str.index[7]], str['CSscore'].loc[str.index[0]], str['CSscore'].loc[str.index[0]], str['CSscore'].loc[str.index[0]]],
    'Last Cur': ['USD', 'USD', 'USD', 'USD','JPY','CHF','CAD'],
    '2nd Value': [str['CSscore'].loc[str.index[0]], str['CSscore'].loc[str.index[0]], str['CSscore'].loc[str.index[0]], str['CSscore'].loc[str.index[0]], str['CSscore'].loc[str.index[4]], str['CSscore'].loc[str.index[3]], str['CSscore'].loc[str.index[6]]]})
    for i in range(0,ds.shape[0]):
        current = ds.iloc[i,:]
        idx = ds.index[i]
        if (((40 >= ds.loc[idx,'1st Value'] or ds.loc[idx,'1st Value'] >= 60) and (40 >= ds.loc[idx,'2nd Value'] or ds.loc[idx,'2nd Value'] >= 60)) and ds.loc[idx,'1st Value'] > ds.loc[idx,'2nd Value'] and abs(ds.loc[idx,'1st Value'] - ds.loc[idx,'2nd Value']) > 20):
            ds.loc[idx,'CSscore'] = 'Bullish'
        elif (((40 >= ds.loc[idx,'1st Value'] or ds.loc[idx,'1st Value'] >= 60) and (40 >= ds.loc[idx,'2nd Value'] or ds.loc[idx,'2nd Value'] >= 60)) and ds.loc[idx,'1st Value'] < ds.loc[idx,'2nd Value'] and abs(ds.loc[idx,'1st Value'] - ds.loc[idx,'2nd Value']) > 20):
            ds.loc[idx,'CSscore'] = 'Bearish'
        else:
            ds.loc[idx,'CSscore'] = 'NA'
    ds = ds.drop(ds[ds.CSscore == 'NA'].index)
    del ds['First Cur']
    del ds['1st Value']
    del ds['Last Cur']
    del ds['2nd Value']
    print (ds)

def market_shift(time_frame,pair,CSscore):
    Symbol = pair
    MS = CSscore
    timezone = pytz.timezone("UTC")
    now = datetime.now(timezone)
    start = datetime.now(timezone) - dt.timedelta(days=5)
    utc_from = datetime(start.year, start.month, start.day)
    utc_to = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
    rates = mt5.copy_rates_range(Symbol, time_frame, utc_from, utc_to)
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
        for i in range(2,htf.shape[0]):
            idx = htf.index[i]
            #Finding the Bullish Market Shift
            if MS == 'Bullish':
                if htf.loc[idx,'Bullish swing'] == True:
                    htf.loc[idx,'Bull1'] = htf['low'].loc[htf.index[i-2]]
                if htf.loc[idx,'Bearish swing'] == True:
                    htf.loc[idx,'Bull2'] = htf['high'].loc[htf.index[i-2]]
                if htf.loc[idx,'Bullish swing'] == True:
                    htf.loc[idx,'Bull3'] = htf['low'].loc[htf.index[i-2]]
            #Finding the Bearish Market Shift
            elif MS == 'Bearish':
                if htf.loc[idx,'Bearish swing'] == True:
                    Bear1 = htf.loc[htf.index[i-2]]
                    htf.loc[idx,'Bear1'] = htf['high'].loc[htf.index[i-2]]
                if htf.loc[idx,'Bullish swing'] == True:
                    htf.loc[idx,'Bear2'] = htf['low'].loc[htf.index[i-2]]
                    Bear2 = htf.loc[htf.index[i-2]]
                if htf.loc[idx,'Bearish swing'] == True:
                    htf.loc[idx,'Bear3'] = htf['high'].loc[htf.index[i-2]]
                    Bear3 = htf.loc[htf.index[i-2]]
    if MS == 'Bullish':
        z = htf['Bull3'].last_valid_index()
        global low
        low = htf['Bull3'].loc[htf.index[z]]
        q = htf['Bull2'].tail(15).dropna()
        try:
            f = q.iloc[-2]
            global high
            high = f
        except:
            f = htf['Bull2'].last_valid_index()
            high = htf['Bull2'].loc[htf.index[f]]
    else:
        z = htf['Bear3'].last_valid_index()
        high = htf['Bear3'].loc[htf.index[z]]
        q = htf['Bear2'].tail(15).dropna()
        try:
            f = q.iloc[-2]
            low = f
        except:
            f = htf['Bear2'].last_valid_index()
            low = htf['Bear2'].loc[htf.index[f]]
    #print ('Price Entry Zone is from', low, 'to', high)

def fvg (time_frame,pair,CSscore):
    Symbol = pair
    MS = CSscore
    timezone = pytz.timezone("UTC")
    now = datetime.now(timezone)
    start = datetime.now(timezone) - dt.timedelta(days=5)
    utc_from = datetime(start.year, start.month, start.day)
    utc_to = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
    rates = mt5.copy_rates_range(Symbol, time_frame, utc_from, utc_to)
    htf = pd.DataFrame(rates)
    htf['time']=pd.to_datetime(htf['time'], unit='s')
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
        global a
        a = (round(Bull_PEP,4))
        global b
        b = (round(Bull_SL,5))
        global c
        c = a + (2*(abs(b-a)))
        print (Symbol,'PEP is:',a,' at:',PEP_time,' SL is:',round(b,4), ' TP is:',round(c,4))
    elif MS == 'Bearish':
        a = (round(Bear_PEP,4)) 
        b = (round(Bear_SL,5))
        c = a - (2*(b-a))
        print (Symbol,'PEP is:',a,' at:',PEP2_time,' SL is:',round(b,4), ' TP is:',round(c,4))

def check_trades(time_frame):
    get_strength(mt5.TIMEFRAME_D1)
    dx = ds.values.tolist()
    for Major_Pair,CSscore in dx:
        market_shift(time_frame,Major_Pair,CSscore)
        fvg(time_frame,Major_Pair,CSscore)
        calc_position_size(Major_Pair,2.0,100)
        open_position(Major_Pair, CSscore, lot_size, a, c, b)

def get_account_info():
    res = mt5.account_info()
    return mt5.account_info()

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

def check_max_drawdown():
    print("Checking maximum drawdown...")
    inital_balance = daily
    max_drawdown = .05
    account_info = get_account_info()
    current_balance = mt5.account_info().balance
    if(current_balance <= (inital_balance)):
        print("Maximum drawdown", inital_balance - (inital_balance*max_drawdown),"has been reached! Trading halted.")
        send_notification("Maximum drawdown has been reached! Trading halted.")

        open_positions = positions_get()
        for index, position in open_positions.iterrows():
            deal_id = position['ticket']
            close_position(deal_id)
        exit()     

def send_notification(message, blocks = None):
    if(blocks is None):
        client.chat_postMessage(channel='#life', text=message)
    else:
        client.chat_postMessage(channel='#life', text=message, blocks=blocks)

def send_stats():
    open_positions = positions_get()
    if(open_positions.empty):
        send_notification("No trades are currently open.")
    else:
        open_positions = open_positions[['time', 'symbol', 'profit','price_open','sl','tp']]
        op = open_positions.values.tolist()
        for time, symbol, profit,price_open,sl,tp in op:
            slack_json = [
            {
                "type": "section",
                "text": {
                "type": "mrkdwn",
                "text": "Open Trade"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Symbol:* " + str(symbol)
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Price Entry:* " + str(price_open)
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Profit:* " + str(profit)
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Time:* " + str(time)
                }
            }
            ]
            send_notification("", slack_json)

def get_daily_trade_data():
    now = datetime.now().astimezone(pytz.timezone('UTC'))
    now = datetime(now.year, now.month, now.day, hour=now.hour, minute=now.minute)
    yesterday = now - timedelta(hours=24)
    res = get_order_history(yesterday, now)
    return res

def send_daily_stats():
    mt5.login(62197811, password="gvfzkub7", server ="MetaQuotes-Demo")
    account_info = mt5.account_info()
    trades = get_daily_trade_data()
    balance = account_info.balance
    # Calculate open trade count
    opened_trades = trades[trades['type'] == 0]
    open_trade_count = opened_trades.shape[0]
    # Calculate closed trade count
    closed_trades = trades[trades['type'] == 1]
    closed_trade_count = closed_trades.shape[0]
    # Calculate profitable trades count
    profitable_trades = trades[trades['profit'] > 0]
    profitable_trades_count = profitable_trades.shape[0]
    # Calculate losing trades count
    losing_trades = trades[trades['profit'] < 0]
    losing_trades_count = losing_trades.shape[0]
    winLossRatio = profitable_trades_count / losing_trades_count
    slack_json = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Daily report"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Account Balance:* " + str(balance)
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Trades opened:* " + str(open_trade_count)
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Trades closed:* " + str(closed_trade_count)
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Profitable trades:* " + str(profitable_trades_count)
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Losing trades:* " + str(losing_trades_count)
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*W/L Ratio:* " + str(winLossRatio)
			}
		}
	]
    send_notification("", slack_json)

def run_trader(time_frame):
    print("Running trader at", datetime.now())
    connect(62197811)
    check_trades(time_frame)

def live_trading():
    schedule.every().day.at("00:00").do(daily_bal)
    schedule.every().hour.at(":00").do(run_trader, mt5.TIMEFRAME_M5)
    schedule.every().hour.at(":15").do(run_trader, mt5.TIMEFRAME_M5)
    schedule.every().hour.at(":30").do(run_trader, mt5.TIMEFRAME_M5)
    schedule.every().hour.at(":45").do(run_trader, mt5.TIMEFRAME_M5)
    schedule.every(3).hours.at(":00").do(send_stats)
    schedule.every().day.at("12:00").do(send_daily_stats)
    schedule.every(15).minutes.do(check_max_drawdown)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    live_trading()