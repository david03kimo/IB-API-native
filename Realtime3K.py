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

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)

    def historicalData(self,reqId,bar):
        print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
        
    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print('-------------------------------------------------------------------------------------------------------------')
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        print('-------------------------------------------------------------------------------------------------------------')
       

    def historicalDataUpdate(self, reqId: int, bar):
        print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
       
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
    app.reqHistoricalData(1,contract,'','1 D','1 min','MIDPOINT',0,1,True,[])
    
    # Call stop() after 3 seconds to disconnect the program
    Timer(30,app.stop).start()
    app.run()

if __name__=="__main__":
    main()
