from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer
import threading
import time
import pandas as pd

class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.data = [] #Initialize variable to store candle
    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)

    def historicalData(self,reqId,bar):
        print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
        self.data.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        df = pd.DataFrame(self.data,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        df['DateTime'] = pd.to_datetime(df['DateTime'],unit='s') 
        df.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/API_Historical.csv',index=0 ,float_format='%.2f')

    def nextValidId(self,orderId):
        self.nextOrderId=orderId
        self.start()

    def start(self):
        
        contract = Contract()
        contract.symbol = "EUR" 
        contract.secType = "CASH" 
        contract.currency = "USD"
        contract.exchange = "IDEALPRO"         


    def stop(self):
        self.reqAccountUpdates(False,"")
        self.done=True
        self.disconnect()


def main():
    app=TestApp()
    app.nextOrderId=0
    app.connect('127.0.0.1',4002,0)
    
    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH" 
    contract.currency = "USD"
    contract.exchange = "IDEALPRO" 

    #request historical data
    app.reqHistoricalData(1,contract,'','1 D','3 mins','MIDPOINT',0,2,False,[]) 

    # Call stop() after 3 seconds to disconnect the program
    Timer(3,app.stop).start()
    app.run()

if __name__=="__main__":
    main()
