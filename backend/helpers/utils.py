from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os


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
    # pass
    # update the .env file with the new key and secret

    return True