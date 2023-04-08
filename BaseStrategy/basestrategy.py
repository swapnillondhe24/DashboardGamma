import backtrader as bt
from backend.helpers.utils import  write_order_to_csv, write_to_log

class baseStrategy(bt.Strategy):
    def notify_trade(self, trade):
        write_to_log("placing trade for {}. target size: {}".format(trade.getdataname(),trade.size))

    def notify_order(self, order):
        write_to_log(order)
        write_order_to_csv(order)
        print(f"Order notification. status{order.getstatusname()}.")
        print(f"Order info. status{order.info}.")
