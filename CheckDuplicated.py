import pandas as pd
import os


data_path='/Users/davidliao/Documents/code/Python/Backtest/data/TF'
output_path='/Users/davidliao/Documents/code/Python/Backtest/report'


# write .h5
pairs_list=[]
for filename in os.listdir(data_path):
    if filename.endswith('.csv') and not filename.endswith('_tmp.csv'):
        pairs_list.append(filename.split('.')[0])
df={}
for pair in range(len(pairs_list)):  
    df[pair]={}
    df[pair]=pd.read_csv(data_path+'/'+pairs_list[pair]+'.csv',parse_dates=['DateTime'])
    df[pair]=pd.DataFrame(df[pair])
    # df[pair]=df[pair].set_index('DateTime')

    print(pairs_list[pair],df[pair][df[pair].duplicated('DateTime')])
