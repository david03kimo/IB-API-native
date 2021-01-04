import numpy as np
import pandas as pd
import talib
from datetime import datetime
import time
import sys

class Indicators():
    def __init__(self):
        return
    
    def SMA(self,df,fast,slow):
        df['sma_fast']=df['Close'].rolling(fast).mean()
        df['sma_slow']=df['Close'].rolling(slow).mean()
        return df

    def MACD(self,DF,a=10,b=20,c=10):
        """function to calculate MACD
        typical values a(fast moving average) = 12; 
                        b(slow moving average) =26; 
                        c(signal line ma window) =9"""
        df = DF.copy()
        df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
        df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
        df["DIF"]=df["MA_Fast"]-df["MA_Slow"]
        df["MACD"]=df["DIF"].ewm(span=c,min_periods=c).mean()
        # df.dropna(inplace=True)
        df=df.drop(["MA_Slow","MA_Fast"],axis=1)
        return df

    def DarkCloudCover1(self,df):  #Dark Cloud Cover
        df['DarkCloudCover']=talib.CDLDARKCLOUDCOVER(df['Open'],df['High'],df['Low'],df['Close'])
        # df['DarkCloudCover']=talib.CDLDARKCLOUDCOVER(df['Open'],df['High'],df['Low'],df['Close'], penetration=0)
        return df

    def EngulfingPattern1(self,df):  #Engulfing Pattern
        df['EngulfingPattern']=talib.CDLENGULFING(df['Open'],df['High'],df['Low'],df['Close'])
        return df

    def PiercingPattern1(self,df):  #Piercing Pattern
        df['PiercingPattern']=talib.CDLPIERCING(df['Open'],df['High'],df['Low'],df['Close'])
        return df

    def bollBnd(self,df,n=20):
        "function to calculate Bollinger Band"
        df = df.copy()
        #df["MA"] = df['close'].rolling(n).mean()
        df['BB_MA'] = df['Close'].ewm(span=n,min_periods=n).mean()
        df['BB_up'] = df['BB_MA'] + 2*df['Close'].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
        df['BB_dn'] = df['BB_MA'] - 2*df['Close'].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
        df['BB_width'] = df['BB_up'] - df['BB_dn']
        # df.dropna(inplace=True)
        # df=df.drop(['BB_width','BB_MA'],axis=1)
        return df

    def RSI(self,DF,n=3):
        "function to calculate RSI"
        df = DF.copy()
        df['delta']=df['Close'] - df['Close'].shift(1)
        df['gain']=np.where(df['delta']>=0,df['delta'],0)
        df['loss']=np.where(df['delta']<0,abs(df['delta']),0)
        avg_gain = []
        avg_loss = []
        gain = df['gain'].tolist()
        loss = df['loss'].tolist()
        for i in range(len(df)):
            if i < n:
                avg_gain.append(np.NaN)
                avg_loss.append(np.NaN)
            elif i == n:
                avg_gain.append(df['gain'].rolling(n).mean()[n])
                avg_loss.append(df['loss'].rolling(n).mean()[n])
            elif i > n:
                avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
                avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
        df['avg_gain']=np.array(avg_gain)
        df['avg_loss']=np.array(avg_loss)
        df['RS'] = df['avg_gain']/df['avg_loss']
        df['RSI'] = 100 - (100/(1+df['RS']))
        return df

    def ATR(self,df,n=14):
        df=df.copy()
        df['High-Low']=abs(df['High']-df['Low'])
        df['High-prevClose']=abs(df['High']-df['Close'].shift(1))
        df['Low-prevClose']=abs(df['Low']-df['Close'].shift(1))
        df['TR']=df[['High-Low','High-prevClose','Low-prevClose']].max(axis=1,skipna=False)
        df['ATR']=df['TR'].rolling(n).mean()
        # df=df.drop(['High-Low','High-prevClose','Low-prevClose','TR'],axis=1)
        return df

class Strategies():
    def __init__(self,StrategyType):
        self.StrategyType=StrategyType
        return
    
    def _BB(self,DF,i):
        action=False
        TakeProfit=0
        StopLoss=0
        ATR_SL=2
        df=DF.copy()
        In=Indicators()
        if self.StrategyType=='API':
            df['ATR']=In.ATR(df)['ATR']
            df['BB_up']=In.bollBnd(df)['BB_up']
            df['BB_dn']=In.bollBnd(df)['BB_dn']
        elif self.StrategyType=='Backtest':
            if not 'ATR' in df.columns:
                df['ATR']=In.ATR(df)['ATR']
                df['BB_up']=In.bollBnd(df)['BB_up']
                df['BB_dn']=In.bollBnd(df)['BB_dn']

        if df['Close'][i-1]>df['BB_dn'][i-1] and df['Close'][i]<=df['BB_dn'][i]:
            action='BUY'
        elif df['Close'][i-1]<df['BB_up'][i-1] and df['Close'][i]>=df['BB_up'][i]:
            action='SELL'
        else:
            action=False

        if action != False:
            TakeProfit=round(df['Close'][i]+ATR_SL*df['ATR'][i],4) if action=='BUY' else round(df['Close'][i]-ATR_SL*df['ATR'][i],4)
            StopLoss=round(df['Close'][i]-ATR_SL*df['ATR'][i],4) if action=='BUY' else round(df['Close'][i]+ATR_SL*df['ATR'][i],4)
        return action,TakeProfit,StopLoss,df

    def _RSI(self,DF,i):
        action=False
        TakeProfit=0
        StopLoss=0
        ATR_SL=2
        df=DF.copy()
        In=Indicators()
        if self.StrategyType=='API':
            df['ATR']=In.ATR(df)['ATR']
            df['RSI']=In.RSI(df)['RSI']
        elif self.StrategyType=='Backtest':
            if not 'ATR' in df.columns:
                df['ATR']=In.ATR(df)['ATR']
                df['RSI']=In.RSI(df)['RSI']
        if df['RSI'][i-1]>20 and df['RSI'][i]<=20:
            action='BUY'
        elif df['RSI'][i-1]<80 and df['RSI'][i]>=80:
            action='SELL'
        else:
            action=False

        if action != False:
            TakeProfit=round(df['Close'][i]+ATR_SL*df['ATR'][i],4) if action=='BUY' else round(df['Close'][i]-ATR_SL*df['ATR'][i],4)
            StopLoss=round(df['Close'][i]-ATR_SL*df['ATR'][i],4) if action=='BUY' else round(df['Close'][i]+ATR_SL*df['ATR'][i],4)
        return action,TakeProfit,StopLoss,df