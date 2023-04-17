import backtrader as bt
import alpaca_backtrader_api as alpaca
import pandas as pd
from datetime import datetime
from backend.helpers.utils import getKey, getSecret,getApi
from BaseStrategy.basestrategy import baseStrategy
from alpaca_trade_api.rest import TimeFrame




api = getApi()



class PaydayEffectStrategy(baseStrategy):
    
    def __init__(self):
        self.buy_day = 16
    
    def next(self):
        print("in next method")
        if self.datas[0].datetime.date().day == self.buy_day:
            self.buy(size=100)
        else :
            self.buy(size=100)
            print("buying in else statement")

symbol = 'GOOGL'
timeframe = 'day'
start_date = '2019-01-01'
end_date = '2022-01-01'

# api = alpaca.AlpacaStore(
#     key_id='YOUR_API_KEY_ID',
#     secret_key='YOUR_SECRET_API_KEY',
#     paper=True
# )

bars = api.get_bars(symbol,TimeFrame.Day, start=start_date, end=end_date)

cerebro = bt.Cerebro()

cerebro.addstrategy(PaydayEffectStrategy)
cerebro.adddata(bt.feeds.PandasData(dataname=bars),name=symbol)

cerebro.broker.setcommission(commission=0.0)
cerebro.broker.setcash(100000.0)

cerebro.run()

port_value = cerebro.broker.getvalue()
pnl = port_value - 100000.0

print(f"Final Portfolio Value: {port_value:,.2f}")
print(f"P/L: {pnl:,.2f}")
