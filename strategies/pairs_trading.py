import alpaca_backtrader_api
import backtrader as bt
import pandas as pd
from datetime import datetime
from backend.helpers.utils import getKey, getSecret, getApi

class pairs_trading(bt.Strategy):
    
    params = dict(
        lookback=20,
        zscore_high=2.0,
        zscore_low=-0.0,
        half_spread=0.01,
        qty1=1000,
        qty2=1000,
        status='out'
    )
    
    def __init__(self):
        self.data1 = self.datas[0]
        self.data2 = self.datas[1]
        
        self.spread = self.data1 - self.data2
        self.spread_ma = bt.indicators.SimpleMovingAverage(self.spread, period=self.params.lookback)
        self.spread_std = bt.indicators.StandardDeviation(self.spread, period=self.params.lookback)
        
    def next(self):
        print("into next method")
        zscore = (self.spread[0] - self.spread_ma[0]) / self.spread_std[0]
        
        if self.params.status == 'out':
            if zscore > self.params.zscore_high:
                self.params.status = 'short'
                self.sell(data=self.data1, size=self.params.qty1)
                self.buy(data=self.data2, size=self.params.qty2)
            elif zscore < self.params.zscore_low:
                self.params.status = 'long'
                self.buy(data=self.data1, size=self.params.qty1)
                self.sell(data=self.data2, size=self.params.qty2)
                print("in first loop second part")
                
        elif self.params.status == 'short' and zscore < 0.0:
            self.params.status = 'out'
            self.buy(data=self.data1, size=self.params.qty1)
            self.sell(data=self.data2, size=self.params.qty2)
            print("buying data1")
            
        elif self.params.status == 'long' and zscore > 0.0:
            self.params.status = 'out'
            self.sell(data=self.data1, size=self.params.qty1)
            self.buy(data=self.data2, size=self.params.qty2)
            print("buying data2")

        else:
            self.buy(data=self.data1, size=self.params.qty1)
            print("buying data1")




if __name__ == '__main__':
    IS_BACKTEST = False
    symbol = 'TSLA'
    symbol1 = "SPY"

    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(pairs_trading)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=getKey(),
        secret_key=getSecret(),
        paper= True,
    )

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    if IS_BACKTEST:
        data = DataFactory(dataname=symbol,
                            historical=True,
                            fromdate=datetime(2020, 7, 1),
                            todate=datetime(2020, 7, 11),
                            timeframe=bt.TimeFrame.Days
                            # data_feed='iex'
                            )
        data0 = DataFactory(dataname=symbol1,
                            historical=True,
                            fromdate=datetime(2020, 7, 1),
                            todate=datetime(2020, 7, 11),
                            timeframe=bt.TimeFrame.Days
                            # data_feed='iex'
                            )
    else:
        data = DataFactory(dataname=symbol,
                            historical=False,
                            timeframe=bt.TimeFrame.Ticks,
                            backfill_start=False
                            # data_feed='iex'
                            )
        data1 = DataFactory(dataname=symbol1,
                            historical=False,
                            timeframe=bt.TimeFrame.Ticks,
                            backfill_start=False
                            # data_feed='iex'
                            )
        # or just alpaca_backtrader_api.AlpacaBroker()
        broker = store.getbroker()
        cerebro.setbroker(broker)
    cerebro.adddata(data,name=symbol)
    cerebro.adddata(data1,name=symbol1)

    if IS_BACKTEST:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.run( live=True)
    print('Final Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    # cerebro.plot()