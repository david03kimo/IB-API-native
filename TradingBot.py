'''
Call signal module after every 3 mins resampling realtime bars and send bracket order if signal is true.
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
from _SB import *

class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.data = [] #Historical
        self.data1 = [] #Update
        self.df=[] # Historical
        self.df1=[] #Update
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

        self.signal=False # For placing Bracket Order
        self.qty=0
        self.entryprice=0
        self.tp=0
        self.sl=0
        self.position=0 # open position

        self.LastReceivedDataTime=int(datetime.now().timestamp())

        return

    def error(self,reqId,errorCode,errorString):
        print(datetime.fromtimestamp(int(datetime.now().timestamp())),'Error: ',reqId,' ',errorCode,' ',errorString)    
        return

    def historicalData(self,reqId,bar):
        self.data.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        self.now_date=int(bar.date)
        return
         
    def historicalDataEnd(self, reqId, start: str, end: str):
        self.data1.append(self.data[-1])
        del self.data[-1]
        self.df = pd.DataFrame(self.data,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        self.df['DateTime'] = pd.to_datetime(self.df['DateTime'],unit='s')
        # self.df.to_csv('/Users/davidliao/Documents/code/Github/IB-native-API/data/3K.csv',index=0 ,float_format='%.5f')   
        # self.data=[] #清掉是否有助於記憶體的節省？
        super().historicalDataEnd(reqId, start, end)
        print( datetime.fromtimestamp(int(datetime.now().timestamp())),'HistoricalDataEnd. ReqId:', reqId, 'from', start, 'to', end)
        return

    def historicalDataUpdate(self, reqId: int, bar):
        self.data1.append([bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume])
        self.LastReceivedDataTime=int(datetime.now().timestamp())
        self.df1 = pd.DataFrame(self.data1,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        self.df1['DateTime'] = pd.to_datetime(self.df1['DateTime'],unit='s') 
        self.df1=self.df1.set_index('DateTime')
        self.pre_date=self.now_date #Calculate the bar.date and previous bar.date
        self.now_date=int(bar.date)

        if self.now_date != self.pre_date : #Resample once after the bar closed
            res_df=self.df1.resample('3min', closed='left', label='left').agg(self.res_dict)
            del self.data1[0:len(self.data1)-1]
            res_df.drop(res_df.index[-1], axis=0, inplace=True) #delete the new open bar at lastest appended row
            # res_df.to_csv('/Users/davidliao/Documents/code/Github/IB-native-API/data/3K.csv', mode='a', header=False,float_format='%.5f')
            # print('Resampled',datetime.fromtimestamp(self.now_date-60*self.period))
            res_df.reset_index(inplace=True)
            self.df = self.df.append(res_df, ignore_index=False) 
            # self.df.to_csv('~/Documents/code/Github/IB native API/data/df.csv',index=0 ,float_format='%.5f')  
            self.signal,self.qty,self.entryprice,self.tp,self.sl=SB(self.df) # call calculation module to get entry sinal and price. can call _SB1 for test.
            if self.signal != False and self.position == 0 : # if entry signal produced and check no position then entry
                self.start()
        return

    def nextValidId(self,orderId):
        self.nextOrderId=orderId
        return

    def start(self):
        contract = Contract() # Contract
        contract.symbol = "EUR"
        contract.secType = "CASH" 
        contract.currency = "USD"
        contract.exchange = "IDEALPRO" 

        bracket = self.BracketOrder(self,self.nextOrderId, self.signal, self.qty, self.entryprice, self.tp, self.sl) # Order
        for o in bracket:
            self.placeOrder(o.orderId, contract, o)
            self.nextOrderId # need to advance this we’ll skip one extra oid, it’s fine

        #Update Portfolio
        self.reqAccountUpdates(True,"") 
        return

    def stop(self):
        self.done=True
        self.disconnect()
        return
    
    @staticmethod
    def BracketOrder(self,
        parentOrderId, #OrderId
        action,  #'BUY' or 'SELL'
        quantity,  #quantity of order
        limitPrice,  # Entry Price
        takeProfitLimitPrice,  # Exit price
        stopLossPrice # Stop-loss price
        ):

        #This will be our main or “parent” order
        parent = Order()
        parent.orderId = parentOrderId
        parent.action = action
        # parent.orderType = 'MKT' #直接下market 單不用擔心沒成交的問題？
        parent.orderType = 'LMT' #直接下market 單不用擔心沒成交的問題？
        parent.totalQuantity = quantity
        parent.lmtPrice = limitPrice
        #The parent and children orders will need this attribute set to False to prevent accidental executions.
        #The LAST CHILD will have it set to True, 
        parent.transmit = False

        takeProfit = Order()
        takeProfit.orderId = parent.orderId + 1
        takeProfit.action = 'SELL' if action == 'BUY' else 'BUY'
        takeProfit.orderType = 'LMT'
        takeProfit.totalQuantity = quantity
        takeProfit.lmtPrice = takeProfitLimitPrice
        takeProfit.parentId = parentOrderId
        takeProfit.transmit = False

        stopLoss = Order()
        stopLoss.orderId = parent.orderId + 2
        stopLoss.action = 'SELL' if action == 'BUY' else 'BUY'
        stopLoss.orderType = 'STP'
        #Stop trigger price
        stopLoss.auxPrice = stopLossPrice
        stopLoss.totalQuantity = quantity
        stopLoss.parentId = parentOrderId
        #In this case, the low side order will be the last child being sent. Therefore, it needs to set this attribute to True 
        #to activate all its predecessors
        stopLoss.transmit = True

        bracketOrder = [parent, takeProfit, stopLoss]
        return bracketOrder
    
    def updatePortfolio(self,contract:Contract,position:float,marketPrice:float,marketValue:float,averageCost:float,unrealizedPNL:float,realizedPNL:float,accountName:str):
        print(datetime.fromtimestamp(int(datetime.now().timestamp())),'UpdatePortfolio.','Symbol:',contract.symbol,'SecType:',contract.secType,'Exchange:',contract.exchange,'Position:',position,'MarketPrice:',marketPrice,'MarketValue:',marketValue,'AverageCost:',averageCost,'UnrealizedPNL:',unrealizedPNL,'RealizedPNL:',realizedPNL,'AccountName:',accountName)
        self.position =position
        return

    def ifDataDelay(self):
        w=180
        while True:
            if int(datetime.now().timestamp()) - self.LastReceivedDataTime >w:
                print(datetime.fromtimestamp(int(datetime.now().timestamp())),w,' sec delayed,last receieved:',datetime.fromtimestamp(self.LastReceivedDataTime))
                self.cancelHistoricalData(1)
                time.sleep(10)
                self.done=True
                self.disconnect()
                time.sleep(10)
                while True:
                    if not self.isConnected():
                        print(datetime.fromtimestamp(int(datetime.now().timestamp())),'Disconnected')
                        raise EOFError
                    time.sleep(10)
            time.sleep(10)
        return

def main():
    print(datetime.fromtimestamp(int(datetime.now().timestamp())),'main() run')
    app=TestApp()
    app.nextOrderId=0
    # app.connect('127.0.0.1',7497,0) # IB TWS
    app.connect('127.0.0.1',4002,0) # IB Gateway
    
    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH" 
    contract.currency = "USD"
    contract.exchange = "IDEALPRO" 

    #request historical data
    app.reqHistoricalData(1,contract,'','2 D','3 mins','MIDPOINT',0,2,True,[])
    t = threading.Thread(target = app.ifDataDelay,name='CheckDelay')
    t.setDaemon(True)
    t.start()        
    app.run()

if __name__=="__main__":
    while True:
        try:
            main()
        except EOFError as e:
            print(datetime.fromtimestamp(int(datetime.now().timestamp())),'main() error due to :',type(e),e)
        time.sleep(10)