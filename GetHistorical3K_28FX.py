'''
Get the historical data
'''


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer
import threading
import time
from datetime import datetime
import pandas as pd

class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.data = [] #Initialize variable to store candle
        self.FX_df={}
        self.pairs_list=['AUDCAD','AUDCHF','AUDJPY','AUDNZD','AUDUSD','CADCHF','CADJPY','CHFJPY','EURAUD','EURCAD','EURCHF','EURGBP','EURJPY','EURNZD','EURUSD','GBPAUD','GBPCAD','GBPCHF','GBPJPY','GBPNZD','GBPUSD','NZDCAD','NZDCHF','NZDJPY','NZDUSD','USDCAD','USDCHF','USDJPY']
        self.count=0

        return

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)
        return

    def historicalData(self,reqId,bar):
        # print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
        self.FX_df[reqId].append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        return

    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print( datetime.fromtimestamp(int(datetime.now().timestamp())),'HistoricalDataEnd. ReqId:', reqId, 'from', start, 'to', end)

        self.FX_df[reqId] = pd.DataFrame(self.FX_df[reqId],columns=['DateTime','Open','High','Low', 'Close','Volume'])
        self.FX_df[reqId]['DateTime'] = pd.to_datetime(self.FX_df[reqId]['DateTime'],unit='s') 
        self.FX_df[reqId].to_csv('/Users/davidliao/Documents/code/Github/IB-native-API/FX_data/'+self.pairs_list[reqId]+'.csv',index=0 ,float_format='%.6f')
        self.count+=1

        if self.count==len(self.pairs_list):
            self.stop()

        return

    def stop(self):
        for pair in range(len(self.pairs_list)):
            self.cancelHistoricalData(pair)
        time.sleep(5)
        self.done=True
        self.disconnect()
        return


def FX_order(symbol):
     contract = Contract()
     contract.symbol = symbol[:3]
     contract.secType = 'CASH'
     contract.exchange = 'IDEALPRO'
     contract.currency = symbol[3:]
     return contract


def main():
    app=TestApp()
    app.nextOrderId=0
    app.connect('127.0.0.1',4002,0)
    
    for pair in range(len(app.pairs_list)):
        contract=FX_order(app.pairs_list[pair])
        app.FX_df[pair]=[]
        print('pairs:',app.pairs_list[pair])
        app.reqHistoricalData(pair,contract,'','1 W','3 mins','MIDPOINT',0,2,False,[]) #request historical data
        
    app.run()

if __name__=="__main__":
    main()
