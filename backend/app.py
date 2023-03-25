import alpaca_backtrader_api
import re
import os
import json
from datetime import datetime
from flask import Flask,send_file,send_from_directory
from flask_restful import Resource, Api
from flask import request,Response
from flask_cors import CORS
try:
    from backend.helpers.utils import saveBrokerInfo as sbi
    from backend.helpers.utils import datadownload,get_file_names, backtest
    from backend.helpers.utils import getApi
except:
    from helpers.utils import saveBrokerInfo as sbi
    from helpers.utils import datadownload,get_file_names, backtest
    from helpers.utils import getApi,Generatecode

api = ''
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Content-Type'


alpaca_api = getApi()

class listExchanges(Resource):
    def listExchanges(self):
        # return alpaca_api.list_assets()
        active_assets = alpaca_api.list_assets(status='active')
        names = {a.exchange for a in active_assets}
        # print(active_assets)
        


        return json.dumps({"exchanges":list(names)}, indent=4)

    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.listExchanges())
            # return Response(request_json)
        except Exception as error:
            print(error)


class listAssets(Resource):
    def listAssets(self,exchange):
        # return alpaca_api.list_assets()
        active_assets = alpaca_api.list_assets(status='active')
        names = {a.symbol for a in active_assets if a.exchange == exchange}
        # print(active_assets)
        


        return json.dumps({"assets":list(names)}, indent=4)

    
    def post(self):
        try:
            request_json = request.get_json()
            exchange = request_json['exchange']
            return Response(self.listAssets(exchange))
            # return Response(request_json)
        except Exception as error:
            print(error)
        
    
        
class getAssets(Resource):
    def getAssets(self,sym):
        return alpaca_api.get_asset(sym)
    
    def post(self):
        try:
            request_json = request.get_json()
            return Response(self.getAssets(request_json['symbol']))
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
        return json.dumps(get_file_names())
    
    def post(self):
        try:
            return Response(self.getNames())

        except Exception as error:
            print(error)



# TODO: BackTesting
class runBacktesting(Resource):
    
    def runBacktesting(self,strategy,symbols,fromdate,todate,cash):
        backtest(strategy,symbols,fromdate,todate,cash)
        return send_from_directory(directory='.',filename='quantstats-tearsheet.html')
    
    def post(self):
        try:
            request_json = request.get_json()
            strategy = request_json['strategy']
            symbols = request_json['symbol']
            fromdate = request_json['fromdate']
            if request_json['todate']:
                todate = request_json['todate']
            if request_json['cash']:
                cash = request_json['cash']

            return Response(self.runBacktesting(strategy,symbols,fromdate,todate,cash))

        except Exception as error:
            print(error)



class runLiveTrading(Resource):
    
    def runLiveTrading(self,strategy,symbol):
        backtest(strategy,symbol)
    
    def post(self):
        try:
            request_json = request.get_json()
            strategy = request_json['strategy']
            data = request_json['data']
            symbol = request_json['symbol']

            return Response(self.runBacktesting(strategy,symbol))

        except Exception as error:
            print(error)


class GenrateCode(Resource):
    def GenrateCode(self,strategy,symbol):
        return Generatecode(strategy,symbol)
    
    def post(self):
        try:
            request_json = request.get_json()
            strategy = request_json['strategy']
            symbol = request_json['symbol']

            return Response(self.GenrateCode(strategy,symbol))

        except Exception as error:
            print(error)


# if __name__ == "__main__":
#     app.run(debug=True)


api.add_resource(listExchanges, '/listexchanges/')
api.add_resource(listAssets, '/listassets/')

api.add_resource(getAssets, '/getassets/')

api.add_resource(saveBrokerInfo, '/savebrokerinfo/')
api.add_resource(DownloadData, '/downloaddata/')
api.add_resource(getNames, '/getnames/')
api.add_resource(GenrateCode, '/generatecode/')
api.add_resource(runBacktesting, '/runbacktesting/')
api.add_resource(runLiveTrading, '/runlivetrading/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5006)
    # app.run(debug=False)