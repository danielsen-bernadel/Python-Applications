from FVG import *
import MetaTrader5 as mt5

#This will need to be updated to take in the date and time from previous script
if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()
mt5.login(41694719, password='qZxitS3Ub701')
timezone = pytz.timezone("UTC")
now = datetime.now(timezone)
start = datetime.now(timezone) - dt.timedelta(days=5)
utc_from = datetime(start.year, start.month, start.day)
utc_to = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
rates = mt5.copy_rates_range(Symbol, mt5.TIMEFRAME_M1, utc_from, utc_to)
htf = pd.DataFrame(rates)
htf['time']=pd.to_datetime(htf['time'], unit='s')
start=time.time()

lot = .01
deviation = 10
if MS == 'Bullish':
    request = {"action": mt5.TRADE_ACTION_PENDING,
                "symbol": Symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "price": a,
                "sl": b,
                "tp": c,
                "deviation": deviation,
                "magic": 00000,
                "comment": "insert comment",
                "type_time": mt5.ORDER_TIME_GTC
                }

if MS == 'Bearish':
    request = {"action": mt5.TRADE_ACTION_PENDING,
                "symbol": Symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "price": a,
                "sl": b,
                "tp": c,
                "deviation": deviation,
                "magic": 00000,
                "comment": "insert comment",
                "type_time": mt5.ORDER_TIME_GTC
                }

# send a trading request
result = mt5.order_send(request)
# check the execution result
print("1. order_send(): by {} {} lots at {} with deviation={} points".format(Symbol,lot,a,deviation));
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("2. order_send failed, retcode={}".format(result.retcode))
    # request the result as a dictionary and display it element by element
    result_dict=result._asdict()
    for field in result_dict.keys():
        print("   {}={}".format(field,result_dict[field]))
        # if this is a trading request structure, display it element by element as well
        if field=="request":
            traderequest_dict=result_dict[field]._asdict()
            for tradereq_filed in traderequest_dict:
                print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
    print("shutdown() and quit")
    mt5.shutdown()
    quit()

print("2. order_send done, ", result)
print("   opened position with POSITION_TICKET={}".format(result.order))
print("   sleep 2 seconds before closing position #{}".format(result.order))
#time.sleep(2)