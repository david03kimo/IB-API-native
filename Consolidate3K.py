'''
Resample the stream tick snapshot data every 3 mins to 3m K
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
from datetime import datetime

class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.data = [] #Historical
        self.data1 = [] #Update
        self.period=3 #3m K
        # resample method dictionary
        self.res_dict = {
            'Open':'first',
            'High':'max',
            'Low':'min',
            'Close': 'last',
            'Volume': 'sum'
            }
        self.now_date=0
        self.pre_date=0

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)

    def historicalData(self,reqId,bar):
        self.data.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        df = pd.DataFrame(self.data,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        df['DateTime'] = pd.to_datetime(df['DateTime'],unit='s') 
        df.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/3K_Historical.csv',index=0 ,float_format='%.5f')


    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print('-------------------------------------------------------------------------------------------------------------')
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        print('-------------------------------------------------------------------------------------------------------------')

    def historicalDataUpdate(self, reqId: int, bar):
        self.data1.append([bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume])
        df1 = pd.DataFrame(self.data1,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        df1['DateTime'] = pd.to_datetime(df1['DateTime'],unit='s') 
        df1=df1.set_index('DateTime')
     
        #Calculate the bar.date and previous bar.date
        self.pre_date=self.now_date
        self.now_date=int(bar.date)
        
        if self.now_date%(self.period*60) ==0 and self.pre_date%(self.period*60)==120 : #Resample once after the bar closed
            res_df=df1.resample('3min', closed='left', label='left').agg(self.res_dict)
            print('Resampled')
            res_df.drop(res_df.index[-1], axis=0, inplace=True) #delete the new open bar at lastest appended row
            res_df.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/res3K_HistoricalUpdate.csv',float_format='%.5f')

        df1.to_csv('/Users/davidliao/Documents/code/Github/MyProject/data/3K_HistoricalUpdate.csv' ,float_format='%.5f')
        
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
    Timer(1500,app.stop).start()
   
    app.run()

if __name__=="__main__":
    main()
