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

    def historicalData(self,reqId,bar):
        print(f'Time: {bar.date} Open:{bar.open} High:{bar.high} Low:{bar.low} Close: {bar.close} Volume: {bar.volume}')
        self.data.append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        df = pd.DataFrame(self.data,columns=['DateTime','Open','High','Low', 'Close','Volume'])
        df['DateTime'] = pd.to_datetime(df['DateTime'],unit='s') 
        df.to_csv('/Users/davidliao/Documents/code/Github/Project1/data/IBAPI_1/API_Historical.csv',index=0 ,float_format='%.2f')
        return df

    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    def historicalDataUpdate(self, reqId: int, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "Close :", bar.close) 
       
    def contractDetails(self,reqId,contractDetails):
        print('contractDetails: ',reqId,' ',contractDetails)    

    def nextValidId(self,orderId):
        self.nextOrderId=orderId
        self.start()

    def orderStatus(self,orderId,status,filled,remaining,avgFillPrice,permId,parenttId,lastFillPrice,clientId,whyHeld,mktCapPrice):
        print('OrderStatus. Id: ',orderId,', Status: ',status,', Filled: ',filled,', Remaining: ',remaining,', LastFillPrice: ',lastFillPrice)
        

    def openOrder(self,orderId,contract,order,orderState):
        print('OpenOrder. ID:',orderId,contract.symbol,contract.secType,'@',contract.exchange,':',order.action,order.orderType,order.totalQuantity, orderState.status)
    
    def execDetails(self,reqId,contract,execution):
        print('ExecDetails. ',reqId,contract.symbol,contract.secType,contract.currency,execution.execId,execution.orderId,execution.shares,execution.lastLiquidity)

    def updatePortfolio(self,contract:Contract,position:float,marketPrice:float,marketValue:float,averageCost:float,unrealizedPNL:float,realizedPNL:float,accountName:str):
        print('UpdatePortfolio.','Symbol:',contract.symbol,'SecType:',contract.secType,'Exchange:',contract.exchange,'Position:',position,'MarketPrice:',marketPrice,'MarketValue:',marketValue,'AverageCost:',averageCost,'UnrealizedPNL:',unrealizedPNL,'RealizedPNL:',realizedPNL,'AccountName:',accountName)

    # def rerouteMktDataReq(self, reqId: int, conId: int, exchange: str):
    #     super().rerouteMktDataReq(reqId, conId, exchange)
    #     print("Re-route market data request. ReqId:", reqId, "ConId:", conId, "Exchange:", exchange) 

    def start(self):
        
        #Update Portfolio
        #self.reqAccountUpdates(True,"")
        
        #contract = Contract()
        #contract.symbol = "EUR" #for historical data 
        #contract.secType = "CASH" 
        #contract.currency = "USD"
        #contract.exchange = "IDEALPRO" 
        
        contract = Contract()
        contract.symbol = "EUR"  #for real-time data
        contract.secType = "CFD" 
        contract.currency = "USD"
        contract.exchange = "SMART" 
    

        #contract=Contract()
        #contract.sumbol="AAPL"
        #contract.secType="STK"
        #contract.exchange="SMART"
        #contract.currency="USD"
        #contract.primaryExchange="NASDAQ"

        order=Order()
        order.action="SELL"
        order.totalQuantity=90000
        order.orderType="MKT"
        #order.lmtPrice=1.2
        

        #self.placeOrder(self.nextOrderId,contract,order)



    def stop(self):
        self.reqAccountUpdates(False,"")
        self.done=True
        self.disconnect()


def main():
    app=TestApp()
    app.nextOrderId=0
    app.connect('127.0.0.1',4002,0)
    
    contract = Contract()
    contract.symbol = "USD"
    contract.secType = "CASH" 
    contract.currency = "JPY"
    contract.exchange = "IDEALPRO" 

    #EClient function
    
    #Contract details
    #app.reqContractDetails(1,contract) 
    

    #request historical data
    app.reqHistoricalData(1,contract,'','1 D','1 min','MIDPOINT',0,2,True,[]) #keepUpToDate = True
    #df = pd.read_csv('/Users/davidliao/Documents/code/Github/IBAPI_1/API_Historical.csv',header=0) 
    
    
    app.df=app.df.iloc[::-1]

    print('The Openp[2] :',app.df.Open.iat[2])

    #print('the close[1] is :',app.bar.close) 


    #request Real-time data
    
    #contract = Contract()
    #contract.symbol = "EUR"  #for real-time data
    #contract.secType = "CFD" 
    #contract.currency = "USD"
    #contract.exchange = "SMART"
    
    #app.rerouteMktDataReq(1,contract,"")

    #app.reqMarketDataType(4) #if live not available,switch to delayed-forzen data.
    #app.reqMktData(1,contract,"",False,False,[])

    # Call stop() after 3 seconds to disconnect the program
    Timer(3,app.stop).start()
    app.run()

if __name__=="__main__":
    main()
