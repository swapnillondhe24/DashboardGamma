import backtrader as bt
import alpaca_backtrader_api
import pandas as pd

from backend.helpers.utils import getKey, getSecret, getApi

class Buy_N_Hold(bt.Strategy):
    
    params = dict(
        symbol = 'MSFT'
    )
    
    def __init__(self):
        self.data = self.getdatabyname(self.params.symbol)
        self.order = None
    
    def next(self):
        print("in next")
        print(self.order)
        print(self.position)
        # self.buy(size=1)
        if self.order:
            return
        
        if self.position:
            self.order = self.buy(size=2)
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Cancelled, order.Rejected]:
            self.order = None

# instantiate the API
# api = alpaca_backtrader_api.AlpacaTrade(key_id=api_key, secret_key=api_secret, base_url=base_url)
if __name__ == "__main__":
    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    apibt = alpaca_backtrader_api.AlpacaStore(
            key_id=getKey(),
            secret_key=getSecret(),
            paper= True,
        )
    api = getApi()

    symbol = 'MSFT'
    timeframe = bt.TimeFrame.Ticks
    last_trade = api.get_latest_trade(symbol)
    print(last_trade)

    data = {
        'open': last_trade.p,
        'high': last_trade.p,
        'low': last_trade.p,
        'close': last_trade.p,
        'volume': last_trade.s
    }

    print(data)
    
    df = pd.DataFrame(data, index=[pd.Timestamp(last_trade.t, unit='s')]).sort_index()
    data = bt.feeds.PandasData(dataname=df)    
    cerebro = bt.Cerebro()
    cerebro.adddata(data,name=symbol)
    cerebro.setbroker(apibt.getbroker())
    cerebro.addstrategy(Buy_N_Hold)
    cerebro.run()
