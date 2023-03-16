from datetime import datetime,timedelta
import json
import os
import backtrader as bt
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
import alpaca_backtrader_api
# from strategies.SmaCross import SmaCross


def getApi():
    load_dotenv()

    API_KEY_ID = os.getenv('API_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
    
    api = tradeapi.REST(API_KEY_ID, SECRET_ACCESS_KEY, base_url='https://paper-api.alpaca.markets' ,api_version='v2')
    
    return api

def getBrokerInfo():
    load_dotenv()
    return os.getenv('BROKER_API_KEY_ID'), os.getenv('BROKER_SECRET_ACCESS_KEY')

def saveBrokerInfo(key,secret):
    import json
    import os

    import dotenv
    try:
        dotenv_path = '../.env'
        if not os.path.exists(dotenv_path):
            with open(dotenv_path, 'w') as f:
                f.write('')
        dotenv.load_dotenv()

        with open(dotenv_path, 'a') as f:
            f.write(f'CLIENT_API_KEY_ID={key}\n')
            f.write(f'CLIENT_SECRET_ACCESS_KEY={secret}\n')

        return json.dumps({'status': 'success'})
    except:
        return json.dumps({'status': 'error'})


def datadownload(symbols,start_date,end_date,timeframe="1D"):
    
    try:    
        if not os.path.exists('../data'):
            os.makedirs('../data')

        for symbol in symbols:
            data = yf.download(symbol, start=start_date, end=end_date,interval=timeframe)
            data.to_csv(f'../data/{symbol}.csv')
        
        return json.dumps({'status': 'success',"filedir":"../data/"})
    
    except Exception as error:
        return json.dumps({'status': 'error',"error_det": str(error)})



def get_file_names(directory_path="../../strategies"):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return []
    else:
        return [os.path.splitext(f)[0] for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]


def getData(symbol,start_date,end_date="datetime.now().strftime('%Y-%m-%d')",timeframe="1D"):
    data = yf.download(symbol, start=start_date, end=end_date,interval=timeframe)
    return data

import pandas as pd

def analyze(strats):
    # Calculate the returns and drawdowns for each strategy
    returns = []
    trades = []
    pyfolio = []
    Sqn = []

    for strat in strats:
        analyzer = strat.analyzers.getbyname('returns')
        returns.append(analyzer.get_analysis())
        analyzer = strat.analyzers.getbyname('trades')
        trades.append(analyzer.get_analysis())
        analyzer = strat.analyzers.getbyname('pyfolio')
        pyfolio.append(analyzer.get_analysis())
        analyzer = strat.analyzers.getbyname('SQN')
        Sqn.append(analyzer.get_analysis())

        analyzer = strat.analyzers.getbyname('pandas_writer')

        df = strat.analyzers.get_analysis()

        print(df)

    
    # total_returns = pd.DataFrame(returns).sum(axis=1)


    exit(0)
    """
    print("returns ",total_returns)
    print("trades",trades)
    print("Pyfolio",pyfolio)
    print("Sqn",Sqn)

    # for strat in strats:
    #     print(dir(strat.analyzers))
    #     print(dir(strat.analyzers.trades))
    #     print(strat.analyzers.trades.rets)

    exit(0)
    # Calculate the other metrics

    num_trades = sum([strat.analyzers.num_trades.total for strat in strats])
    win_rate = sum([strat.analyzers.won.total for strat in strats]) / num_trades
    avg_win = sum([strat.analyzers.win.total for strat in strats]) / sum([strat.analyzers.won.total for strat in strats])
    avg_loss = sum([strat.analyzers.loss.total for strat in strats]) / sum([strat.analyzers.lost.total for strat in strats])
    # max_drawdown = total_drawdowns.min()
    sharpe_ratio = bt.analyzers.SharpeRatio().get_analysis()['sharperatio']
    """
    # Create and return the analysis dictionaryw
    analysis = {
        'total_returns': total_returns,

        'num_trades': num_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        # 'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio
    }
    return analysis


def write_to_log(msg):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("logfile.txt", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')


def backtest(strategy, data=0, symbol="",fromdate="", todate=0, cash=10000):

    alpaca_api = getApi()
    load_dotenv()
    
    fromdate=parse_date(fromdate)
    

    if not todate:
        todate = datetime.now() - timedelta(minutes=20)
    else:
        todate = parse_date(todate)

    # exit(0)

    import importlib

    

    # The module name is two levels up
    module_name = "strategies."+str(strategy)

    # Get the module object dynamically
    module = importlib.import_module(module_name, package=__package__)

    # Get the class object by name
    class_name = str(strategy)
    strategy_class = getattr(module, class_name)


    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    cerebro = bt.Cerebro()

    # Setup Store
    store = alpaca_backtrader_api.AlpacaStore(
        key_id=os.getenv('API_KEY_ID'),
        secret_key=os.getenv('SECRET_ACCESS_KEY'),
        paper= True
    )
    

    DataFactory = store.getdata  
    if not data:    
        data0 = DataFactory(dataname=symbol,
                            historical=True,
                            fromdate=fromdate,
                            todate=todate,
                            timeframe=bt.TimeFrame.Days,
                            data_feed='iex')
    else:
        data0 = data
        
    broker = store.getbroker()

    cerebro.setbroker(broker)
    cerebro.adddata(data0)
    
    cerebro.addstrategy(strategy_class)
    from backtrader.analyzers import PandasWriter
    #add Analyzers
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    
    
  
    alpaca_api = getApi()
    accinfo = alpaca_api.get_account()
    initial_cash = float(accinfo.effective_buying_power)-float(accinfo.equity)


    print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    strats = cerebro.run()


    # return analyze(strats)
    pnl = cerebro.broker.getvalue() - initial_cash
    print('Final Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    
    return pnl
    # return analyze(strats=strats)

"""
example usage
    res = backtest("SmaCross",symbol="GOOG",fromdate=datetime(2020,7,1))
    print("****************************************************************")
    print(res)

O/P
    46363.75 (profit made by strategy)


"""



if __name__=="__main__":
    
    res = backtest("SmaCross",symbol="GOOGL",fromdate="2020-09-21",todate="2020-10-21")
    print("****************************************************************")
    print(res)
    # print(get_file_names())