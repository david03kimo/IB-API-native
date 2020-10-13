import pandas as pd
import talib
from SendBracketOrder import sendorder

quantity=20807.121237394185
action='SELL'
Limit=1.18224
TakeProfit=1.1815190929687551
StopLoss=1.1829609070312448
sendorder(action,Limit,quantity,TakeProfit,StopLoss)
# print(s,quantity,Limit,TakeProfit,StopLoss)

    