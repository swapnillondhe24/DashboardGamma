from datetime import datetime,timedelta
import json
import os
import backtrader as bt
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
import alpaca_backtrader_api
import json
import quantstats as qs
# from strategies.SmaCross import SmaCross


def getApi():
    load_dotenv()

    API_KEY_ID = os.getenv('API_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
    
    api = tradeapi.REST(API_KEY_ID, SECRET_ACCESS_KEY, base_url='https://paper-api.alpaca.markets' ,api_version='v2')
    
    return api


def getKey():
    load_dotenv()
    return os.getenv('API_KEY_ID')

def getSecret():
    load_dotenv()
    return os.getenv('SECRET_ACCESS_KEY')


def getBrokerInfo():
    load_dotenv()
    return os.getenv('CLIENT_API_KEY_ID'), os.getenv('CLIENT_SECRET_ACCESS_KEY')

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



def get_file_names(directory_path="../strategies"):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return []
    else:
        ret_lst = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        ret_lst.remove("__init__")
        return ret_lst


def getData(symbol,start_date,end_date="datetime.now().strftime('%Y-%m-%d')",timeframe="1D"):
    data = yf.download(symbol, start=start_date, end=end_date,interval=timeframe)
    return data

import pandas as pd



#TODO def getdata from file and display code


import json

def Generatecode(filename,symbol):
    filename = "./strategies/"+filename
    k,s = getBrokerInfo()
    alpaca_key = "ALPACA_KEY = "+k
    alpaca_secret = "ALPACA_SECRET = "+s
    symbol = "SYMBOL = "+symbol
    strategy = "STRATEGY = "+filename
    print("been here")

    try:
        with open(filename + ".py", 'r') as file:
            file_contents = file.read()
            # Replace specific parameters inside the file with new values
            file_contents = file_contents.replace('ALPACA_KEY = ""', alpaca_key)
            file_contents = file_contents.replace('ALPACA_SECRET = ""', alpaca_secret)
            file_contents = file_contents.replace('SYMBOL = ""', symbol)
            file_contents = file_contents.replace('STRATEGY = ""', strategy)
            # Return updated file contents as a JSON string
            return json.dumps({"code": file_contents})
        

    except FileNotFoundError:
        return json.dumps({'status': 'error'})


def write_to_log(msg):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("logfile.json", "a+") as f:
        f.write(f"[{timestamp}] {msg}\n")


def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')


def backtest(strategy, symbols="",fromdate="", todate=0, cash=10000):

    # alpaca_api = getApi()
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

    # Create an instance of the class
    
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class)

    cerebro.broker.setcommission(commission=0.001)

    datapath = 'FB.csv'

    data = []

    # symbol = "GOOGL"
    # symbol2 = "TSLA"

    # data = bt.feeds.PandasData(dataname=yf.download(symbol, '2017-01-01', '2022-01-10'))
    # data0 = bt.feeds.PandasData(dataname=yf.download(symbol2, '2017-01-01', '2022-01-10'))

    for s in symbols:
        data.append(bt.feeds.PandasData(dataname=yf.download(s, fromdate, todate)))

    for d in data:
        cerebro.adddata(d)

    cerebro.broker.setcash(100000.0)

    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="return")
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    strat_return = strat.analyzers.getbyname("return").get_analysis()
    strat_return = list(strat_return.items())
    idx, values = zip(*strat_return)
    strat_return = pd.Series(values, idx)

    output_name = strategy + ".html"
    return qs.reports.full(strat_return)
    # return analyze(strats=strats)

"""
example usage
    res = backtest("SmaCross",symbol="GOOG",fromdate=datetime(2020,7,1))
    print("****************************************************************")
    print(res)

O/P
    46363.75 (profit made by strategy)


"""

#TODO def live trading

def live_trading():
    pass



# backtest("pairs_trading",data=["GOOGL","TSLA"],fromdate="2020-09-21",todate="2020-10-21")

if __name__=="__main__":
    # 
    # backtest("pairs_trading",symbols=["SPY","GOOGL"],fromdate="2021-09-21")
    write_to_log(Generatecode("SmaCross", "AAPL"))
    print("****************************************************************")
    print(datetime.now())
    # print(get_file_names())