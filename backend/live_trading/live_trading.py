
try:
    from live_trading.live_trading_calculations import get_all_positions, unrealised_profit_df_strategy, realized_profit_df_strategy, get_pnl_df_strategy, get_all_positions
except:
    from backend.live_trading.live_trading_calculations import get_all_positions, unrealised_profit_df_strategy, realized_profit_df_strategy, get_pnl_df_strategy, get_all_positions




import json
from flask import Flask
from flask_restful import Resource, Api
from flask import request,Response
from flask_cors import CORS
# from helpers.tradeinfo import run_processes



api = ''
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Content-Type'



class getPositions(Resource):
    def getPositons(self):
        return get_all_positions()
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getPositons(), mimetype="text/event-stream")
            # return Response(request_json)
        except Exception as error:
            print(error)
            

class unrealisedprofitdfstrategy(Resource):
    def getUnrealizedPnl(self):
        transaction_json = json.dumps(unrealised_profit_df_strategy(), indent=4)
        return transaction_json
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getUnrealizedPnl(), mimetype="text/event-stream")
            # return Response(request_json)
        except Exception as error:
            print(error)
            
class realizedProfitDfStrategy(Resource):
    def getRealizedPnl(self):
        transaction_json = json.dumps(realized_profit_df_strategy(), indent=4)
        return transaction_json
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getRealizedPnl(), mimetype="text/event-stream")
            # return Response(request_json)
        except Exception as error:
            print(error)
            
class getpnldfstrategy(Resource):
    def getPnlStrategy(self):
        return get_pnl_df_strategy(unrealised_profit_df_strategy(),realized_profit_df_strategy())
    
    def post(self):
        try:
            # request_json = request.get_json()
            return Response(self.getPnlStrategy())
            # return Response(request_json)
        except Exception as error:
            print(error)

            
# def run_live_strategy():
     
# if __name__ == "__main__":
#     app.run(debug=True)
        
# api.add_resource(run_live_strategy, '/runlivestrategy/')
api.add_resource(getPositions, '/getPositions/')
api.add_resource(getpnldfstrategy, '/getpnlstrategy/')
api.add_resource(realizedProfitDfStrategy, '/getrealizedpnl/')
api.add_resource(unrealisedprofitdfstrategy, '/getunrealizedpnl/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5009)