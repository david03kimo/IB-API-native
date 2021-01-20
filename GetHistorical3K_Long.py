'''
Get 28 pairs of FX 3m data about 13 year till no data provided from IB
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
        self.pairs_list=['AUDCAD','AUDCHF','AUDJPY','AUDNZD','AUDUSD','CADCHF','CADJPY','CHFJPY','EURAUD','EURCAD','EURCHF','EURGBP','EURJPY','EURNZD','EURUSD','GBPAUD','GBPCAD','GBPCHF','GBPJPY','GBPNZD','GBPUSD','NZDCAD','NZDCHF','NZDJPY','NZDUSD','USDCAD','USDCHF','USDJPY']
        self.count=0
        self.PairsCount=0
        self.QueryTime=''
        self.ifPlot= True
        self.path='/Users/davidliao/Documents/code/Python/Backtest/data/TF'
        self.FX_df={}
        self.FX_df1={}
        self.tmp_df={}
        for pair in range(len(self.pairs_list)):
            self.FX_df[pair]={}
            self.FX_df[pair][0]=[]
            self.FX_df1[pair]=[]
        self.LastReceivedDataTime=int(datetime.now().timestamp())
        self.pairs_list1=[]
        self.tmp=[]
        for filename in os.listdir(self.path):
            if filename.endswith('.csv'):
                self.pairs_list1.append(filename.split('.')[0])
            if '_tmp' in filename:
                self.tmp.append(filename.split('.')[0])
        
        if self.tmp:
            self.tmp_df=pd.read_csv(self.path+'/'+self.tmp[0]+'.csv',parse_dates=['DateTime'])
            self.tmp_df=pd.DataFrame(self.tmp_df)
            self.QueryTime=datetime.strftime(self.tmp_df['DateTime'][0],'%Y%m%d %H:%M:%S GMT')

            self.FX_df1[self.PairsCount]=self.tmp_df

            self.pairs_list1.remove(self.tmp[0])
            set1=set(self.pairs_list) 
            set2=set(self.pairs_list1) 
            self.pairs_list=list(set1-set2)
            self.pairs_list.remove(self.tmp[0].split('_tmp')[0])    
            self.pairs_list.insert(0,self.tmp[0].split('_tmp')[0])
        else:
            set1=set(self.pairs_list) 
            set2=set(self.pairs_list1) 
            self.pairs_list=list(set1-set2)

        return

    def error(self,reqId,errorCode,errorString):
        if errorCode == 366 and self.PairsCount<len(self.pairs_list):
            self.start()
        elif errorCode == 366 and self.PairsCount==len(self.pairs_list):
            print(datetime.fromtimestamp(int(datetime.now().timestamp())),'over(366)')
            self.stop()
        
        if errorCode == 162 and self.PairsCount<len(self.pairs_list):
            self.FX_df1[self.PairsCount].to_csv(self.path+'/'+self.pairs_list[self.PairsCount]+'.csv',index=0 ,float_format='%.6f')
            self.FX_df1[self.PairsCount]=[] #  release RAM
            if self.tmp:
                if self.pairs_list[self.PairsCount] == self.tmp[0].split('_tmp')[0]:
                    print(datetime.fromtimestamp(int(datetime.now().timestamp())),'delete tmp file:',self.tmp[0],'.csv')
                    os.remove(self.path+'/'+self.tmp[0]+'.csv')
                    self.tmp=[]
                    
            self.PairsCount+=1
            self.count=0
            self.FX_df[self.PairsCount][self.count]=[]
            self.FX_df1[self.PairsCount]=[]
            self.QueryTime=''
            if self.PairsCount <len(self.pairs_list):
                self.start()
            else:
                print(datetime.fromtimestamp(int(datetime.now().timestamp())),self.pairs_list,'Get Data Process Over.')                
                if self.ifPlot:
                    PlotData()
                self.stop()

        if errorCode == 1100 or errorCode == 2107 or errorCode == 502 or errorCode == 504:
            if not self.FX_df1[self.PairsCount].empty:
                self.FX_df1[self.PairsCount].to_csv(self.path+'/'+self.pairs_list[self.PairsCount]+'_tmp.csv',index=0 ,float_format='%.6f')
                print(datetime.fromtimestamp(int(datetime.now().timestamp())),'save',self.pairs_list[self.PairsCount],'_tmp.csv')

        if errorCode == 1102:
            self.LastReceivedDataTime=int(datetime.now().timestamp())
        
        if errorCode != 366 and errorCode != 162:
            print(datetime.fromtimestamp(int(datetime.now().timestamp())),'Error: ',reqId,' ',errorCode,' ',errorString)

        return

    def historicalData(self,reqId,bar):
        self.FX_df[self.PairsCount][reqId].append([bar.date, bar.open,bar.high,bar.low,bar.close,bar.volume])
        self.LastReceivedDataTime=int(datetime.now().timestamp())
        return

    def historicalDataEnd(self, reqId, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print(datetime.fromtimestamp(int(datetime.now().timestamp())),'Pair:',self.pairs_list[self.PairsCount],' HistoricalDataEnd. ReqId:', reqId, 'from', start, 'to', end)
        self.cancelHistoricalData(reqId)
        self.FX_df[self.PairsCount][reqId] = pd.DataFrame(self.FX_df[self.PairsCount][reqId],columns=['DateTime','Open','High','Low', 'Close','Volume'])
        self.FX_df[self.PairsCount][reqId]['DateTime'] = pd.to_datetime(self.FX_df[self.PairsCount][reqId]['DateTime'],unit='s') 

        self.FX_df1[self.PairsCount]=self.FX_df[self.PairsCount][reqId].append(self.FX_df1[self.PairsCount],ignore_index=True)
        # self.FX_df1[self.PairsCount].to_csv(self.path+'/'+self.pairs_list[self.PairsCount]+'_test.csv',index=0 ,float_format='%.6f')
        # print(self.FX_df1[self.PairsCount])
        self.QueryTime=datetime.strftime(self.FX_df1[self.PairsCount]['DateTime'][0],'%Y%m%d %H:%M:%S GMT')
        self.FX_df[self.PairsCount][reqId]=[] # release RAM
        
        self.count+=1
        self.FX_df[self.PairsCount][self.count]=[]
        
        return
        
    def start(self):
        contract=FX_order(self.pairs_list[self.PairsCount])
        self.reqHistoricalData(self.count,contract,self.QueryTime,'1 W','3 mins','MIDPOINT',0,2,False,[])

    def stop(self):
        self.done=True
        self.disconnect()
        return
    
    def ifDataDelay(self):
        w=300 # wait for seconds
        while True:
            if int(datetime.now().timestamp()) - self.LastReceivedDataTime >w:
                print(datetime.fromtimestamp(int(datetime.now().timestamp())),w,' sec delayed,last receieved:',datetime.fromtimestamp(self.LastReceivedDataTime))
                self.cancelHistoricalData(self.count)
                time.sleep(3)
                if not self.FX_df1[self.PairsCount].empty:
                    self.FX_df1[self.PairsCount].to_csv(self.path+'/'+self.pairs_list[self.PairsCount]+'_tmp.csv',index=0 ,float_format='%.6f')
                    print(datetime.fromtimestamp(int(datetime.now().timestamp())),'save',self.pairs_list[self.PairsCount],'_tmp.csv')
                self.stop()
                while True:
                    if not self.isConnected():
                        print(datetime.fromtimestamp(int(datetime.now().timestamp())),'Disconnected')
                        raise EOFError
                    time.sleep(2)
            time.sleep(10)
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
    app.connect('127.0.0.1',4002,1) # IB Gateway
    # app.connect('127.0.0.1',7497,0) # IB TWS 
    t = threading.Thread(target = app.ifDataDelay,name='CheckDelay_GetData')
    t.setDaemon(True)
    t.start()        
    app.start()
    app.run()

if __name__=="__main__":
    while True:
        try:
            main()
        except EOFError as e:
            print(datetime.fromtimestamp(int(datetime.now().timestamp())),'main() error due to :',type(e),e)
        time.sleep(10)
