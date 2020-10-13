'''
This is for webhook listener to call to send order to IB.
'''

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum
from threading import Timer
class TestApp(EWrapper,EClient):
    def __init__(self,signal,entryprice,qty,tp,sl):
        EClient.__init__(self,self)
        self.signal=signal
        self.entryprice=entryprice
        self.qty=qty
        self.tp=tp
        self.sl=sl
        return

    def error(self,reqId,errorCode,errorString):
        print('Error: ',reqId,' ',errorCode,' ',errorString)
        return

    def nextValidId(self,orderId):
        self.nextOrderId=orderId
        self.start()
        return

    def orderStatus(self,orderId,status,filled,remaining,avgFillPrice,permId,parenttId,lastFillPrice,clientId,whyHeld,mktCapPrice):
        print('OrderStatus. Id: ',orderId,', Status: ',status,', Filled: ',filled,', Remaining: ',remaining,', LastFillPrice: ',lastFillPrice)
        return
        
    def openOrder(self,orderId,contract,order,orderState):
        print('OpenOrder. ID:',orderId,contract.symbol,contract.secType,'@',contract.exchange,':',order.action,order.orderType,order.totalQuantity, orderState.status)
        return
    
    def execDetails(self,reqId,contract,execution):
        print('ExecDetails. ',reqId,contract.symbol,contract.secType,contract.currency,execution.execId,execution.orderId,execution.shares,execution.lastLiquidity)
        return

    def updatePortfolio(self,contract:Contract,position:float,marketPrice:float,marketValue:float,averageCost:float,unrealizedPNL:float,realizedPNL:float,accountName:str):
        print('UpdatePortfolio.','Symbol:',contract.symbol,'SecType:',contract.secType,'Exchange:',contract.exchange,'Position:',position,'MarketPrice:',marketPrice,'MarketValue:',marketValue,'AverageCost:',averageCost,'UnrealizedPNL:',unrealizedPNL,'RealizedPNL:',realizedPNL,'AccountName:',accountName)
        return

    def start(self):
        #EURUSD sell 10000 0
        #{{ticker}} {{strategy.order.action}} {{strategy.order.contracts}} {{strategy.position_size}}
        # print('data is ',self.data)

        # self.data=self.data.split()
        # self.data = [x.upper() for x in self.data]
        # action=self.data[1]
        # print('Action:',action)
        # quantity=int(self.data[2])
        # print('Quantity:',quantity)
        #position=int(self.data[3])
        # print('Position:',position)

        # Contract
        contract = Contract()
        contract.symbol = 'EUR'
        contract.secType = 'CFD' 
        contract.currency = 'USD'
        contract.exchange = 'SMART' 

        # Order
        bracket = self.BracketOrder(self.nextOrderId(), self.signal, self.qty, self.entryprice, self.tp, self.sl)
        for o in bracket:
            self.placeOrder(o.orderId, contract, o)
            self.nextOrderId() # need to advance this we’ll skip one extra oid, it’s fine

        #Update Portfolio
        self.reqAccountUpdates(True,"") 
        return
        
    def stop(self):
        self.reqAccountUpdates(False,"")
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
        parent.orderType = 'LMT'
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

def sendorder(signal,price,qty,limit,stop):
    app=TestApp(signal,price,qty,limit,stop)
    app.nextOrderId=0
    app.connect('127.0.0.1',4002,0)

    # Call stop() after 3 seconds to disconnect the program
    Timer(3,app.stop).start()
    
    app.run()

if __name__=="__main__":
    main()