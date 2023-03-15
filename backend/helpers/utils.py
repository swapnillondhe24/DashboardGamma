from datetime import datetime
import json
import os
import backtrader as bt
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
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





def backtest(strategy, data="", symbol="",fromdate="", todate="", cash=10000):

    import importlib

    # The module name is two levels up
    module_name = "strategies.SmaCross"

    # Get the module object dynamically
    module = importlib.import_module(module_name, package=__package__)

    # Get the class object by name
    class_name = "SmaCross"
    strategy_class = getattr(module, class_name)

    
    if todate=="":
        todate = datetime.now().strftime("%Y-%m-%d")
    
    if data == "":
        data = getData(symbol,fromdate,todate)
    
    if data.empty and fromdate=="":
        fromdate = pd.to_datetime(data.index[0]).strftime('%Y-%m-%d') 

    if data.empty  and todate=="":
        todate = pd.to_datetime(data.index[-1]).strftime('%Y-%m-%d')

    feed = bt.feeds.PandasData(dataname=data)

    # print(strategy)
    # exit(0)
    print(feed)
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class)
    cerebro.adddata(feed)
    cerebro.broker.set_cash(cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=90)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addanalyzer(bt.analyzers.DrawDown)

    cerebro.addwriter(bt.WriterFile, csv=True, out='results.csv')

    strats = cerebro.run()
    print("******Reached Here***********")

    # bar_data_res = .analyzers.getbyname('pyfolio')
    # df = pd.DataFrame(bar_data_res)
    # print(df)
    


    pyfoliozer = strats[0].analyzers.getbyname('pyfolio')
    tradeanalyzer = strats[0].analyzers.getbyname('tradeanalyzer')
    drawdown = strats[0].analyzers.getbyname('drawdown')

    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()


    results = {
        
        'returns': returns.tolist(),
        'positions': positions,
        'transactions': transactions,
        'gross_lev': gross_lev.tolist(),
        'trade_analysis': tradeanalyzer.get_analysis().to_dict(),
        'drawdown': drawdown.get_analysis().to_dict()
    }

    print(results)

    # logs = cerebro.runstr()
    results_json = json.dumps(results)
    # logs_json = json.dumps(logs)

    return (results)


if __name__=="__main__":
    print(backtest("SmaCross",symbol="AAPL",fromdate="2020-01-01"))
    # print(get_file_names())