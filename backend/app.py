import alpaca_backtrader_api
import re
import os
import json
from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask import request,Response
from flask_cors import CORS

from helpers.utils import saveBrokerInfo as sbi
from helpers.utils import datadownload,get_file_names, backtest

api = ''
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Content-Type'

from helpers.utils import getApi

alpaca_api = getApi()

class listAssets(Resource):
    def listAssets(self):
        # return alpaca_api.list_assets()
        active_assets = alpaca_api.list_assets(status='active')
        names = [a.exchange for a in active_assets]
        # print(active_assets)


        return json.dumps(names, indent=4)

    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.listAssets())
            # return Response(request_json)
        except Exception as error:
            print(error)
        
    
        
class getAssets(Resource):
    def getAssets(self,sym):
        return alpaca_api.get_asset(sym)
    
    def post(self):
        try:
            request_json = request.get_json()
            if request_json['symbol']:
                return Response(self.getAssets(request_json['symbol']))
            else:
                return Response(self.getAssets())
            # return Response(request_json)
        except Exception as error:
            print(error)
            


            

class saveBrokerInfo(Resource):
    
    def saveBrokerInfo(self,key,secret):
        return sbi(key,secret)
    
    def post(self):
        try:
            request_json = request.get_json()
            key,secret = request_json['key'],request_json['secret']
            
            return Response(self.saveBrokerInfo(key,secret))
                
            # return Response(request_json)
        except Exception as error:
            print(error)
            


class DownloadData(Resource):
    
    def DownloadData(self,symbols,start_date,end_date,timeframe):
        return datadownload(symbols,start_date,end_date,timeframe)
    
    def post(self):
        try:
            request_json = request.get_json()
            symbols = request_json['symbols']
            start_date = request_json['start_date']
            if request_json['end_date']:
                end_date = request_json['end_date']
            else:
                end_date = datetime.now().strftime("%Y-%m-%d")

            if request_json['timeframe']:
                timeframe = request_json['timeframe']
            else:
                timeframe = "1d"
            
            return Response(self.DownloadData(symbols,start_date,end_date,timeframe))

        except Exception as error:
            print(error)







# TODO: Add a function to populate strategy list 10-3
class getNames(Resource):
    
    def getNames(self):
        return get_file_names()
    
    def post(self):
        try:
            return Response(self.getNames())

        except Exception as error:
            print(error)


# TODO: Add a function to return stratey code accodring to strategy name

# TODO: BackTesting
class runBacktesting(Resource):
    
    def runBacktesting(self,strategy,data,symbol,fromdate,todate,cash):
        return backtest(strategy,data,symbol,fromdate,todate,cash)
    
    def post(self):
        try:
            request_json = request.get_json()
            strategy = request_json['strategy']
            data = request_json['data']
            symbol = request_json['symbol']
            fromdate = request_json['fromdate']
            todate = request_json['todate']
            cash = request_json['cash']

            return Response(self.runBacktesting(strategy,data,symbol,fromdate,todate,cash))

        except Exception as error:
            print(error)

# TODO: LiveTrading


# if __name__ == "__main__":
#     app.run(debug=True)


api.add_resource(listAssets, '/listassets/')
api.add_resource(getAssets, '/getassets/')
api.add_resource(saveBrokerInfo, '/savebrokerinfo/')
api.add_resource(DownloadData, '/downloaddata/')
api.add_resource(getNames, '/getnames/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5006)
    # app.run(debug=False)