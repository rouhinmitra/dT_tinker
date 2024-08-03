#%%
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error 
import seaborn as sns
#%% 
"""
Experiments to compare dT vs LST per station
Plot timeseries
Check how the slopes vary for single stations

"""
def read_files(dir_flux):
    """
    Read amerflux merged data from folder: 
    """
    temp=[]
    file_name=[]
    os.chdir(dir_flux)
    flux_list=os.listdir()
    for index in range(len(flux_list)):
        temp.append(pd.read_csv(flux_list[index]))
    return temp

#%%
dir="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_calculated\\"
dt_data=read_files(dir)


# %%
for i in range(len(dt_data)):
    if dt_data[i].shape[0]>=100:
        print(dt_data[i].Veg.iloc[0],dt_data[i].Name.iloc[0],dt_data[i].shape[0],dt_data[i].State.iloc[0],i)
# len(dt_data)

# %%
