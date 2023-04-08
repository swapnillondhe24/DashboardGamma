import csv
from datetime import datetime,timedelta
import json
from multiprocessing import Process
import multiprocessing
import os
import subprocess
import backtrader as bt
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
import alpaca_backtrader_api
import json
import quantstats as qs
import matplotlib
import pandas as pd
matplotlib.use('Agg')

# from strategies.SmaCross import SmaCross



##############################################################################################
###################     INDEX : API and CSV Related Functions     ############################
##############################################################################################

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


def write_to_log(msg,strategy):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("resources/"+strategy +"_logfile.txt", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")



def get_latest_order(apil = getApi()):
    positions = apil.get_activities(page_size=1)
    return apil.get_order(positions[0].order_id)


def write_order_to_csv(order, filename="/resources/orders.csv"):
    headers = ['order_id', 'symbol', 'qty', 'side', 'type', 'time_in_force', 'submitted_at', 'filled_at', 'filled_qty', 'filled_avg_price']
    

    order = get_latest_order()

    file_exists = os.path.isfile(filename)


    
    with open(filename, mode='w+', newline='') as order_file:
        writer = csv.DictWriter(order_file, fieldnames=headers)
        
        if not file_exists:
            writer.writeheader()
            
        try:
            writer.writerow({
            'order_id': order['id'],
            'symbol': order['symbol'],
            'qty': order['qty'],
            'side': order['side'],
            'type': order['type'],
            'time_in_force': order['time_in_force'],
            'submitted_at': str(order['submitted_at']),
            'filled_at': str(order['filled_at']) if order['filled_at'] else '',
            'filled_qty': order['filled_qty'] if order['filled_qty'] else 0,
            'filled_avg_price': order['filled_avg_price']
            })
        except:
            writer.writerow({
            'order_id': order.id,
            'symbol': order.symbol,
            'qty': order.qty,
            'side': order.side,
            'type': order.type,
            'time_in_force': order.time_in_force,
            'submitted_at': str(order.submitted_at),
            'filled_at': str(order.filled_at) if order.filled_at else '',
            'filled_qty': order.filled_qty if order.filled_qty else 0,
            'filled_avg_price': order.filled_avg_price
            })
        
        order_file.close()
        
    write_order_details_to_json(filename)


def write_order_details_to_json(filepath):
    api = getApi()
    order_details = []
    with open(filepath, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # skip header row
        for row in csv_reader:
            order_id = row[0]
            order = api.get_order(order_id)
            order_dict = {
                'order ID': order.id,
                'Symbol': order.symbol,
                'Qty': order.qty,
                'filled_qty': order.filled_qty,
                'Type': order.side,
                'side': order.side,
                'time_in_force': order.time_in_force,
                'Status': order.status,
                'Price': order.filled_avg_price,
                'Time': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }
            order_details.append(order_dict)
            
    transactions = {"transaction": order_details}
    
    
            
    with open('resources/transaction.json', 'a+') as outfile:
        json.dump(transactions, outfile)






##############################################################################################
###################     INDEX : Client Broker information storing     ########################
##############################################################################################


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





##############################################################################################
###################     INDEX : Downloading Data to .csv API endpoint function     ###########
##############################################################################################


def datadownload(symbols,start_date,end_date,timeframe="1D"):
    
    try:    
        if not os.path.exists('data'):
            os.makedirs('data')

        for symbol in symbols:
            data = yf.download(symbol, start=start_date, end=end_date,interval=timeframe)
            data.to_csv(f'data/{symbol}.csv')
        
        return json.dumps({'status': 'success',"filedir":"../data/"})
    
    except Exception as error:
        return json.dumps({'status': 'error',"error_det": str(error)})



#  instead of downloading return it as a dataframe

def getData(symbol,start_date,end_date="datetime.now().strftime('%Y-%m-%d')",timeframe="1D"):
    data = yf.download(symbol, start=start_date, end=end_date,interval=timeframe)
    return data



##############################################################################################
###################  INDEX : Return Files names present in stratigies folder     #############
##############################################################################################


def get_file_names(directory_path="strategies"):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return []
    else:
        ret_lst = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        ret_lst.remove("__init__")
        return ret_lst






##############################################################################################
###################  INDEX : Generate Code Function      #####################################
##############################################################################################

import json

def Generatecode(filename,symbol):
    filename = "./templates/"+filename
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




##############################################################################################
###################  INDEX : Backtesting and Related Functions      ##########################
##############################################################################################

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')


def backtest(strategy, symbols="",fromdate="", todate=0, cash=10000):

    # alpaca_api = getApi()
    load_dotenv()
    
    fromdate=parse_date(fromdate)
    

    if  todate == 0:
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

    # datapath = 'FB.csv'

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
    return qs.reports.html(strat_return, output=output_name, title="Backtest Report")


##############################################################################################
###################  INDEX : Live Trading and Related Functions    ###########################
##############################################################################################

# Global Variables
backend_process = None
trading_process = None

def start_backend():

    print("Starting Backend")
    try:
        subprocess.run("python live_trading.py",cwd="backend/live_trading",shell=True)
    except ImportError:
        subprocess.run("python live_trading.py",cwd="backend/live_trading",shell=True)
    except KeyboardInterrupt:
        exit(0)

ALPACA_API_KEY = getKey()
ALPACA_SECRET_KEY = getSecret()
ALPACA_PAPER = True  # set to False for live trading
TIMEFRAME = bt.TimeFrame.Ticks

def get_alpaca_data(symbol, timeframe):
    
    alpaca_api = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=ALPACA_PAPER,
        usePolygon=False
    )

    alpaca_data = alpaca_backtrader_api.AlpacaData(
        dataname=symbol,
        timeframe=timeframe,
        store=alpaca_api,
        fromdate=datetime(2022, 1, 1),
        todate=datetime.now(),
        historical=True,
        qcheck=0.5,
        backfill_start=True,
        backfill=True
    )

    return alpaca_data

# define function to run live trading
def run_live_trading(strategy_function, symbol):
    cerebro = bt.Cerebro()

    # add strategy
    strategy = strategy_function()
    cerebro.addstrategy(strategy)

    # add data
    alpaca_data = get_alpaca_data(symbol, TIMEFRAME)
    cerebro.adddata(alpaca_data)

    # set broker
    cerebro.broker = alpaca_backtrader_api.AlpacaBroker(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=ALPACA_PAPER
    )

    # set commission
    cerebro.broker.setcommission(
        commission=0.0,
        margin=1.0,
        mult=1.0,
        name=None
    )

    # run live trading
    cerebro.run()







def live_trading(run_func,symbol):
    global backend_process
    global trading_process
    multiprocessing.set_start_method("fork")

    try:
        backend_process = Process(target=start_backend)

        trading_process = Process(target=run_live_trading,args=(run_func ,symbol))

        trading_process.start()
        backend_process.start()

        trading_process.join()
        backend_process.join()

    except KeyboardInterrupt:
        backend_process.terminate()
        trading_process.terminate()


def stop_trading():
    global backend_process
    global trading_process

    if backend_process is not None:
        backend_process.terminate()
    if trading_process is not None:
        trading_process.terminate()



if __name__=="__main__":
    # 
    # backtest("pairs_trading",symbols=["SPY","GOOGL"],fromdate="2021-09-21")
    # write_to_log(Generatecode("SmaCross", "AAPL"))
    live_trading("SmaCross","AAPL")
    print("****************************************************************")
    print(datetime.now())
    # print(get_file_names())
# backtest("pairs_trading",data=["GOOGL","TSLA"],fromdate="2020-09-21",todate="2020-10-21")