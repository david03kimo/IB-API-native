'''
Under construction
'''
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum
from threading import Timer
import pandas as pd
import threading
import time

class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.data = []
        self.data1 = []

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)

    def historicalData(self,reqId,bar):
        print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
        #self.df=pd.DataFrame(self.df,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        #self.df.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        #self.df['DateTime'] = pd.to_datetime(self.df['DateTime'],unit='s') 
        
        self.data.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        df = pd.DataFrame(self.data,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        df['DateTime'] = pd.to_datetime(df['DateTime'],unit='s') 
        df.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/3K_Historical.csv',index=0 ,float_format='%.5f')


    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print('-------------------------------------------------------------------------------------------------------------')
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        print('-------------------------------------------------------------------------------------------------------------')
        #self.df.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/3K_Historical.csv',index=0 ,float_format='%.2f')

    def historicalDataUpdate(self, reqId: int, bar):
        print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
        #self.df.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        #self.df['DateTime'] = pd.to_datetime(self.df['DateTime'],unit='s') 
        #self.df.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/3K_Historical.csv',index=0 ,float_format='%.2f')

        self.data1.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        df1 = pd.DataFrame(self.data1,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        df1['DateTime'] = pd.to_datetime(df1['DateTime'],unit='s') 
        # df2=df1.resample('3min', label='left').agg({'DateTime':first,'Open': first, 'High': max, 'Low': min, 'Close': last,'Volume': last})
        # df2=df1.resample('3min', label='left').agg({'DateTime':'first','Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last','Volume': 'mean'})

        df1.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/3K1_Historical.csv',index=0 ,float_format='%.5f')
        #df2.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/3K1_Historical.csv',index=0 ,float_format='%.5f')

    def nextValidId(self,orderId):
        self.nextOrderId=orderId
        self.start()

    def start(self):
        order=Order()
        order.action="SELL"
        order.totalQuantity=90000
        order.orderType="MKT"

    def stop(self):
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
    app.reqHistoricalData(1,contract,'','1 D','1 min','MIDPOINT',0,2,True,[])

    # Call stop() after 3 seconds to disconnect the program
    Timer(60,app.stop).start()
   
    app.run()

if __name__=="__main__":
    main()
