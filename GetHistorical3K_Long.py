'''
Get 28 pairs of FX 3m data about 10 month.(max from IB)
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
        self.FX_df={}
        self.pairs_list=['AUDCAD','AUDCHF','AUDJPY','AUDNZD','AUDUSD','CADCHF','CADJPY','CHFJPY','EURAUD','EURCAD','EURCHF','EURGBP','EURJPY','EURNZD','EURUSD','GBPAUD','GBPCAD','GBPCHF','GBPJPY','GBPNZD','GBPUSD','NZDCAD','NZDCHF','NZDJPY','NZDUSD','USDCAD','USDCHF','USDJPY']
        self.count=0
        self.PairsCount=0
        self.QueryTime=''
        return

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)
        return

    def historicalData(self,reqId,bar):
        self.FX_df[reqId].append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        return

    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print( datetime.fromtimestamp(int(datetime.now().timestamp())),'HistoricalDataEnd. ReqId:', reqId, 'from', start, 'to', end)
        self.cancelHistoricalData(reqId)
        self.FX_df[reqId] = pd.DataFrame(self.FX_df[reqId],columns=['DateTime','Open','High','Low', 'Close','Volume'])
        self.FX_df[reqId]['DateTime'] = pd.to_datetime(self.FX_df[reqId]['DateTime'],unit='s') 
        # self.FX_df[reqId].to_csv('/Users/davidliao/Documents/code/Github/Backtest_Python/data/TF/'+'EURUSD'+str(reqId)+'.csv',index=0 ,float_format='%.6f')
        
        self.QueryTime=datetime.strftime(self.FX_df[reqId]['DateTime'][0],'%Y%m%d %H:%M:%S GMT')
        self.count+=1
        self.FX_df[self.count]=[]    
        if reqId == 41:
            for i in range(reqId-1,-1,-1):
                self.FX_df[reqId]=self.FX_df[reqId].append(self.FX_df[i],ignore_index=True)
            self.FX_df[reqId].to_csv('/Users/davidliao/Documents/code/Github/Backtest_Python/data/TF/'+self.pairs_list[self.PairsCount]+'.csv',index=0 ,float_format='%.6f')
            
            self.PairsCount+=1
            self.count=0
        self.start()

    def start(self):
        if self.PairsCount==28:
            self.stop()
            return
        
        contract=FX_order(self.pairs_list[self.PairsCount])
        self.reqHistoricalData(self.count,contract,self.QueryTime,'1 W','3 mins','MIDPOINT',0,2,False,[])

    def stop(self):
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
    app.FX_df[0]=[]  
    # app.connect('127.0.0.1',4002,0) # IB Gateway
    app.connect('127.0.0.1',7497,0) # IB TWS 
    app.start()  
    app.run()

if __name__=="__main__":
    main()
