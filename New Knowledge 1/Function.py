#Import Necessary Libaries for script
def Library():    
    from pytz import timezone
    import matplotlib.pyplot as plt
    import pandas as pd
    import time
    import datetime as dt
    from datetime import datetime
    import MetaTrader5 as mt5
    import pytz
    import talib
    import numpy

    utc_tz = pytz.timezone('UTC')
    pd.set_option('display.max_columns', 500) # number of columns to be displayed
    pd.set_option('display.width', 1500)      # max table width to display

    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()
    mt5.login()

    timezone = pytz.timezone("UTC")
    now = datetime.now(timezone)
Library()