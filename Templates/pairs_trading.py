import alpaca_backtrader_api
import backtrader as bt
import pandas as pd
from datetime import datetime


class pairs_trading(bt.Strategy):
    
    params = dict(
        lookback=20,
        zscore_high=2.0,
        zscore_low=-2.0,
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
                
        elif self.params.status == 'short' and zscore < 0.0:
            self.params.status = 'out'
            self.buy(data=self.data1, size=self.params.qty1)
            self.sell(data=self.data2, size=self.params.qty2)
            
        elif self.params.status == 'long' and zscore > 0.0:
            self.params.status = 'out'
            self.sell(data=self.data1, size=self.params.qty1)
            self.buy(data=self.data2, size=self.params.qty2)

