import json
import os

import alpaca_trade_api as tradeapi
from dotenv import load_dotenv


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


def datadownload(symbols,start_date,end_date,timeframe):
    import yfinance as yf
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
        return [os.path.splitext(f)[0] for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
