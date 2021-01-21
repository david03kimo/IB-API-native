import pandas as pd
import os


input_path='/Users/davidliao/Documents/code/Python/Backtest/data/TF'
output_path='/Users/davidliao/Documents/code/Python/Backtest/data/h5'


# read .csv

input_list=[]
for filename in os.listdir(input_path):
    if filename.endswith('.csv') and not filename.endswith('_tmp.csv'):
        input_list.append(filename.split('.')[0])

output_list=[]
for filename in os.listdir(output_path):
    if filename.endswith('.h5'):
        output_list.append(filename.split('.')[0])

print(len(input_list),input_list)
print(len(output_list),output_list)

set1=set(input_list) 
set2=set(output_list) 
pairs_list=list(set1-set2)
print('Convert? ',pairs_list)
input()
# read .h5
# for filename in os.listdir(input_path):
#     if filename.endswith('.h5'):
#         input_list.append(filename.split('.')[0])

# put into dataframe    
df={}
for pair in range(len(pairs_list)):  
    df[pair]={}
    # read from .csv
    df[pair]=pd.read_csv(input_path+'/'+pairs_list[pair]+'.csv',parse_dates=['DateTime'])
    df[pair]=pd.DataFrame(df[pair])
    df[pair]=df[pair].set_index('DateTime')

    # read from .h5
    # df[pair]=pd.read_hdf(output_path+'/'+input_list[pair]+'.h5', 'df') 
    # df[pair]=pd.DataFrame(df[pair])
    
    # write .h5
    df[pair].to_hdf(output_path+'/'+pairs_list[pair]+'.h5', key='df', mode='w') 
    df[pair]={}

    # write .csv
    # df[pair].to_csv(output_path+'/'+input_list[pair]+'.csv',index=1 ,float_format='%.4f')



