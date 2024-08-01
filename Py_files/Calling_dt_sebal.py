#%%
import pandas as pd 
import numpy as np 
import os

st=pd.read_csv("D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Station_List\\Ameriflux_dT_stations.csv", encoding='unicode_escape')
# Convert start year to date (setting it to January 1st)
st['start_date'] = st["AmeriFlux BASE Start"].astype(str) + '-01-01'
# Convert end year to date (setting it to December 31st to represent the full year)
st['end_date'] = st["AmeriFlux BASE End"].astype(str) + '-12-31'
print(st)
# base_directory = 'D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_sebal\\'
# os.makedirs(base_directory, exist_ok=True)
# for row in range(st["Site ID"].shape[0]):
#        # Create a folder name (replace or remove invalid characters)
#     folder_name =st["Site ID"].iloc[row]    
#     # Create the full path for the new folder
#     folder_path = os.path.join(base_directory, folder_name)
#         # Create the folder
#     os.makedirs(folder_path, exist_ok=True)
#     print(f"Created folder: {folder_path}")
# print("All folders have been created.")
st[st["Site ID"]=="US-Var"]
#%%
import sys 
import os
import importlib
sys.path.append(os.path.abspath("D:\\Backup\\Rouhin_Lenovo\\US_project\\geeSEBAL_Tinker\\Py_files\\"))
import sebal as sebal
# import Sen_ls_merge as sls
importlib.reload(sebal) 
# def call_et_func(lon,lat,start_date,end_date,scale,name,dir):
for st_index in range(34,st.shape[0]):
    print(st["Site ID"].iloc[st_index])
    sebal.call_et_func(st.Long.iloc[st_index],st.Lat.iloc[st_index],st["start_date"].iloc[st_index],\
                   st["end_date"].iloc[st_index],30,st["Site ID"].iloc[st_index],"D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_sebal\\")
# st["Site ID"].iloc[0]
