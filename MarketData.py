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
        self.data = [] #Initialize variable to store candle
    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)

    def tickPrice(self,reqId,tickType,price,attrib):
        print('Tick Price.Ticker Id:',reqId,'tickType:',TickTypeEnum.to_str(tickType),'Price:',price,end=' ')

    def tickSize(self,reqId,tickType,size):
        print('Tick Size. Ticker Id:',reqId,'tickType:',TickTypeEnum.to_str(tickType),'Size:',size)

    # def start(self):
        
        
    def stop(self):
        self.reqAccountUpdates(False,"")
        self.done=True
        self.disconnect()

def main():
    app=TestApp()
    app.nextOrderId=0
    app.connect('127.0.0.1',4002,0)

    #request Real-time data
    contract = Contract()
    contract.symbol = "EUR"  #for real-time data
    contract.secType = "CFD" 
    contract.currency = "USD"
    contract.exchange = "SMART"
    
    app.reqMarketDataType(4) #if live not available,switch to delayed-forzen data.
    app.reqMktData(1,contract,"",False,False,[])

    # Call stop() after 3 seconds to disconnect the program
    #Timer(60,app.stop).start()
    
    app.run()

if __name__=="__main__":
    main()