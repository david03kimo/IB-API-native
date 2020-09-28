'''
This is for check the balance to verify if order placing correct!

'''
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum
from threading import Timer

class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)

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

    def start(self):
        contract = Contract()
        contract.symbol = "EUR"  #for real-time data
        contract.secType = "CFD" 
        contract.currency = "USD"
        contract.exchange = "SMART" 

        order=Order()
        order.action="SELL"
        order.totalQuantity=80000
        order.orderType="MKT"

        # self.placeOrder(self.nextOrderId,contract,order)

        #Update Portfolio
        self.reqAccountUpdates(True,"") 
        
        

    def stop(self):
        self.reqAccountUpdates(False,"")
        self.done=True
        self.disconnect()

def main():
    app=TestApp()
    app.nextOrderId=0
    app.connect('127.0.0.1',4002,0)

    # Call stop() after 3 seconds to disconnect the program
    Timer(3,app.stop).start()
    
    app.run()

if __name__=="__main__":
    main()