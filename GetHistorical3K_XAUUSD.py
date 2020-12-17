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
        self.CMDTY_df={}
        self.pairs_list=['XAUUSD']
        self.count=0

        return

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)
        return

    def historicalData(self,reqId,bar):
        # print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
        self.CMDTY_df[reqId].append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        return

    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print( datetime.fromtimestamp(int(datetime.now().timestamp())),'HistoricalDataEnd. ReqId:', reqId, 'from', start, 'to', end)

        self.CMDTY_df[reqId] = pd.DataFrame(self.CMDTY_df[reqId],columns=['DateTime','Open','High','Low', 'Close','Volume'])
        self.CMDTY_df[reqId]['DateTime'] = pd.to_datetime(self.CMDTY_df[reqId]['DateTime'],unit='s') 
        self.CMDTY_df[reqId].to_csv('/Users/davidliao/Documents/code/Github/IB-native-API/data/CMDTY_data/'+self.pairs_list[reqId]+'.csv',index=0 ,float_format='%.6f')
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

def Commodity(symbol):
    contract = Contract()
    contract.symbol = symbol
    # contract.symbol = symbol[:3]
    contract.secType = 'CMDTY'
    contract.exchange = 'SMART'
    contract.currency = symbol[3:]
    return contract


def main():
    app=TestApp()
    app.nextOrderId=0
    # app.connect('127.0.0.1',4002,0) # IB Gateway
    app.connect('127.0.0.1',7497,0) # IB TWS
    
    for pair in range(len(app.pairs_list)):
        contract=Commodity(app.pairs_list[pair])
        app.CMDTY_df[pair]=[]
        print('pairs:',app.pairs_list[pair])
        app.reqHistoricalData(pair,contract,'','1 W','3 mins','MIDPOINT',0,2,False,[]) #request historical data
        
    app.run()

if __name__=="__main__":
    main()
