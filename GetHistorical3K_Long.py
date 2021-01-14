'''
Get 28 pairs of FX 3m data about 10 month.(max from IB)
'''

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer
import threading
import time
from datetime import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.style

class TestApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.pairs_list=['AUDCAD']
        # self.pairs_list=['AUDCAD','AUDCHF','AUDJPY','AUDNZD','AUDUSD','CADCHF','CADJPY','CHFJPY','EURAUD','EURCAD','EURCHF','EURGBP','EURJPY','EURNZD','EURUSD','GBPAUD','GBPCAD','GBPCHF','GBPJPY','GBPNZD','GBPUSD','NZDCAD','NZDCHF','NZDJPY','NZDUSD','USDCAD','USDCHF','USDJPY']
        self.count=0
        self.PairsCount=0
        self.QueryTime=''
        self.MaxReq=41 # max numbers of weeks to get
        self.ifPlot= True
        self.path='/Users/davidliao/Documents/code/Github/Backtest_Python/data/TF'
        self.FX_df={}
        for pair in range(len(self.pairs_list)):
            self.FX_df[pair]={}
            for count in range(self.MaxReq+1):
                self.FX_df[pair][count]=[]
        return

    def error(self,reqId,errorCode,errorString):
        if errorCode == 366 and self.PairsCount<len(self.pairs_list):
            self.start()
        elif errorCode == 366 and self.PairsCount==len(self.pairs_list):
            self.stop()
        
        if errorCode == 162:
            print('errorCode 162')
            self.stop()

        if errorCode != 366:
            print('Error: ',reqId,' ',errorCode,' ',errorString)
        return

    def historicalData(self,reqId,bar):
        self.FX_df[self.PairsCount][reqId].append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        return

    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print('Pair:',self.pairs_list[self.PairsCount],' HistoricalDataEnd. ReqId:', reqId, 'from', start, 'to', end)
        self.cancelHistoricalData(reqId)
        self.FX_df[self.PairsCount][reqId] = pd.DataFrame(self.FX_df[self.PairsCount][reqId],columns=['DateTime','Open','High','Low', 'Close','Volume'])
        self.FX_df[self.PairsCount][reqId]['DateTime'] = pd.to_datetime(self.FX_df[self.PairsCount][reqId]['DateTime'],unit='s') 
        # self.FX_df[self.PairsCount][reqId].to_csv(self.path+self.pairs_list[self.PairsCount]+str(reqId)+'.csv',index=0 ,float_format='%.6f')
        
        self.QueryTime=datetime.strftime(self.FX_df[self.PairsCount][reqId]['DateTime'][0],'%Y%m%d %H:%M:%S GMT')
        self.count+=1
        self.FX_df[self.PairsCount][self.count]=[]
        if reqId == self.MaxReq:
            for i in range(reqId-1,-1,-1):
                self.FX_df[self.PairsCount][reqId]=self.FX_df[self.PairsCount][reqId].append(self.FX_df[self.PairsCount][i],ignore_index=True)
            
            self.FX_df[self.PairsCount][reqId].to_csv(self.path+'/'+self.pairs_list[self.PairsCount]+'.csv',index=0 ,float_format='%.6f')
            
            self.PairsCount+=1
            self.count=0
            self.QueryTime=''
        return
        
    def start(self):
        contract=FX_order(self.pairs_list[self.PairsCount])
        self.reqHistoricalData(self.count,contract,self.QueryTime,'1 W','3 mins','MIDPOINT',0,2,False,[])

    def stop(self):
        self.done=True
        self.disconnect()
        app=TestApp()
        if app.ifPlot:
            PlotData()
        return

def PlotData():
    app=TestApp()
    pairs_list=[]
    for filename in os.listdir(app.path):
        if filename.endswith('.csv'):
            pairs_list.append(filename.split('.')[0])
    df={}
    for pair in range(len(pairs_list)):
        df[pair]=pd.read_csv(app.path+'/'+pairs_list[pair]+'.csv',parse_dates=['DateTime'])
        df[pair]=pd.DataFrame(df[pair])
        df[pair]['DateTime'] = pd.to_datetime(df[pair]['DateTime'],unit='s') 
        df[pair]=df[pair].set_index('DateTime')
        plt.figure(figsize=(24,8))
        plt.plot(df[pair]['Close'],color='black')
        plt.xlabel(pairs_list[pair],fontsize=18)
        plt.ylabel('Price',fontsize=18)
    plt.show()   


def FX_order(symbol):
     contract = Contract()
     contract.symbol = symbol[:3]
     contract.secType = 'CASH'
     contract.exchange = 'IDEALPRO'
     contract.currency = symbol[3:]
     return contract

def main():
    app=TestApp()
    # app.connect('127.0.0.1',4002,0) # IB Gateway
    app.connect('127.0.0.1',7497,0) # IB TWS 
    app.start()
    app.run()

if __name__=="__main__":
    main()
