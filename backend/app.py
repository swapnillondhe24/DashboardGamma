import alpaca_backtrader_api
import re
import os
import json
from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask import request,Response
from flask_cors import CORS



api = ''
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Content-Type'

from helpers.utils import getApi, saveBrokerInfo

api = getApi()

class listAssets(Resource):
    def listAssets(self):
        return api.list_asset()
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.listAssets())
            # return Response(request_json)
        except Exception as error:
            print(error)
        
    
        
class getAssets(Resource):
    def getAssets(self,sym):
        return api.get_asset(sym)
    
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
        return saveBrokerInfo(key,secret)
    
    def post(self):
        try:
            request_json = request.get_json()
            key,secret = request_json['key'],request_json['secret']
            
            return Response(self.saveBrokerInfo(key,secret))
                
            # return Response(request_json)
        except Exception as error:
            print(error)
            
# TODO: Data Download yfinance 10-3 
# TODO: Add a function to populate strategy list 10-3
# TODO: Add a function to return stratey code accodring to strategy name
# TODO: BackTesting
# TODO: LiveTrading




     
# if __name__ == "__main__":
#     app.run(debug=True)


api.add_resource(listAssets, '/listassets/')
api.add_resource(getAssets, '/getassets/')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
    app.run(debug=False)