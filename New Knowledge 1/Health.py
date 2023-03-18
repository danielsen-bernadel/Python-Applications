import mt5
import MetaTrader5

mt5.initialize()

a = mt5.symbol_info_tick('EURUSD').ask
print(a)