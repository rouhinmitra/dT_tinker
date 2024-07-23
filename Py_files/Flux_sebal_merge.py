#%%
import pandas as pd 
import os 
import numpy as np 
dir_bif="D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\Csv_Files\\AF_dT_unzip_BIF\\"
dir_flux="D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\Csv_Files\\AF_dT_unzip\\"
dir_sebal="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_sebal\\"


def read_bif(dir_bif):
    """
    Read metadata which is called BIF
    """
    temp=[]
    os.chdir(dir_bif)
    bif_list=os.listdir()
    for index in range(len(bif_list)):
        temp.append(pd.read_excel(bif_list[index]))

    return temp, bif_list


def read_flux(dir_flux):
    """
    Read amerflux main data from folder: 
    """
    temp=[]
    os.chdir(dir_flux)
    flux_list=os.listdir()
    for index in range(len(flux_list)):
        temp.append(pd.read_csv(flux_list[index], encoding='utf-8',skiprows=2))

    return temp, flux_list

def add_state(list_main,list_state):
    """
    TO merge the two we need to change local timezones to GMT 
    Why? Because Landsat times are in GMT so we will do the merging in that
    Therefore to find timezones we need the 
    """
    

    return 

def read_sebal():
    """
    Read sebal
    """


    return 

def merge_inst_sebal():
    """
    Merge during landsat overpass 
    """

    return 

bif_files,bif_filenames=read_bif(dir_bif)
flux_files,flux_filenames=read_flux(dir_flux)

#%%
bif_files[0][bif_files[0]["VARIABLE_GROUP"]=="GRP_STATE"]["DATAVALUE"].iloc[0]
bif_filenames[0].split("_")[1]
# filename.split('_', 2) 
# bif_filenames[0]
# temp
#%%

