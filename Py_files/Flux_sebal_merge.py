#%%
import os 
import numpy as np 
import pandas as pd
import pytz

dir_bif="D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\Csv_Files\\AF_dT_unzip_BIF\\"
dir_flux="D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\Csv_Files\\AF_dT_unzip\\"
dir_sebal="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_sebal\\"
out_dir_sebal="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_sebal_processed\\"

def read_bif(dir_bif):
    """
    Read metadata which is called BIF
    """
    temp=[]
    file_name=[]
    os.chdir(dir_bif)
    bif_list=os.listdir()
    for index in range(len(bif_list)):
        temp.append(pd.read_excel(bif_list[index]))
        file_name.append(bif_list[index].split("_")[1])
    return temp, file_name


def read_flux(dir_flux):
    """
    Read amerflux main data from folder: 
    """
    temp=[]
    file_name=[]
    os.chdir(dir_flux)
    flux_list=os.listdir()
    for index in range(len(flux_list)):
        temp.append(pd.read_csv(flux_list[index], encoding='utf-8',skiprows=2))
        file_name.append(flux_list[index].split("_")[1])

    return temp, file_name



def add_state(main_list,metadata_list,file_name_main,file_name_metadata):
    """
    TO merge the two we need to change local timezones to GMT 
    Why? Because Landsat times are in GMT so we will do the merging in that
    Therefore to find timezones we need the 
    """
    for main_list_index in range(len(main_list)):
        for metadata_index in range(len(metadata_list)):
            if file_name_main[main_list_index]==file_name_metadata[metadata_index]:
                main_list[main_list_index]["State"]=metadata_list[metadata_index][metadata_list[metadata_index]["VARIABLE_GROUP"]=="GRP_STATE"]["DATAVALUE"].iloc[0]
                main_list[main_list_index]["Name"]=file_name_main[main_list_index]
                # main_list[main_list_index]["Dae"]=pd.to_datetime(main_list[main_list_index]["TIMESTAMP_START"])

    return main_list



def process_sebal_outputs(dir_sebal):
    """
    Concatenate sebal outputs and stuff them into single csv's
    """
    file_name=[]
    sebal_st=[]
    os.chdir(dir_sebal)
    sebal_list=os.listdir()
    for index in range(len(sebal_list)):
        temp=[]
        os.chdir(dir_sebal+sebal_list[index]+"\\")
        file_list=os.listdir()
        for j in file_list:
            temp.append(pd.read_csv(j))
        pd.concat(temp).to_csv(out_dir_sebal+sebal_list[index]+".csv")
        sebal_st.append(pd.concat(temp))
    return sebal_st,sebal_list



def read_sebal(dir_sebal):
    """
    Read sebal
    """
    temp=[]
    file_name=[]
    os.chdir(dir_sebal)
    sebal_list=os.listdir()
    for index in range(len(sebal_list)):
        temp.append(pd.read_csv(sebal_list[index]))
        file_name.append(sebal_list[index].split(".")[0])
    return temp, file_name



def convert_timezone_gmt(df, state):
    """
    Function to convert insitu datetime to GMT
    """
    pacific_states = ["WA", "OR", "NV", "CA"]
    mountain_states = ["AZ", "WY", "UT", "CO", "NM", "ID", "MT"]
    central_states = ["OK", "AR", "IL", "ND", "WI", "AL", "KS", "MO", "TX", "NE", "MN", "IA", "LA", "MS", "SD", "TN"]
    
    if state in pacific_states:
        tz = pytz.timezone('US/Pacific')
    elif state in mountain_states:
        tz = pytz.timezone('US/Mountain')
    elif state in central_states:
        tz = pytz.timezone('US/Central')
    else:
        tz = pytz.timezone('US/Eastern')

    df["Datetime"] = pd.to_datetime(df["TIMESTAMP_START"], format='%Y%m%d%H%M')
    df["Datetime_Local_flux"] = df["Datetime"].dt.tz_localize(tz, nonexistent='shift_forward', ambiguous=False)
    df["Datetime_GMT"] = df["Datetime_Local_flux"].dt.tz_convert('GMT')
    return df



def column_names_sebal(df):
    """
    Change the column names to avoid _x and _y annotations
    """
    df= df.rename(columns={"NDVI":"NDVI_model","G":"Ginst","LE":"LEinst","H":"Hinst"})
    df["LE_daily_orig"]=df["ET_24h"]*28.36
    return df 

def column_names_flux(df):
    """
    Column names have Var_1_1_1 or something else. 
    Change those column names to a unique name for all the files
    Variables we need to calculate dT: H, Ta, PA,USTAR, ZL, RH, MO_LENGTH*(may not be in all files)
    Ancilliary variables which maybe needed: LE, WS
    """
    ## Get a list of the variables 
    LE=sorted([col for col in df.columns if "LE"==col.split("_")[0]],key=len)
    H=sorted([col for col in df.columns if "H"==col.split("_")[0]],key=len)
    # G=sorted([col for col in df.columns if "G"==col.split("_")[0]],key=len)
    MO_L=sorted([col for col in df.columns if "MO_LENGTH" in col],key=len)
    Ufric=sorted([col for col in df.columns if "USTAR" in col],key=len)
    ZL=sorted([col for col in df.columns if "ZL" in col],key=len)
    RH=sorted([col for col in df.columns if "RH"==col.split("_")[0]],key=len)
    WS=sorted([col for col in df.columns if "WS"==col.split("_")[0]],key=len)
    PA=sorted([col for col in df.columns if "PA"==col.split("_")[0]],key=len)
    TA=sorted([col for col in df.columns if "TA"==col.split("_")[0]],key=len)
    # Choose the most occuring variables except  for H,LE,G where we choose the first one from a list 
    df=df.rename(columns={LE[0]:"LE_inst_af",H[0]:"H_inst_af"})
    # print(Ufric,ZL,RH,WS,PA,TA)
    # Ufric_min=df[Ufric].isna().sum().idxmin()
    if (len(MO_L)!=0) & (len(RH)!=0):
        df=df.rename(columns={df[Ufric].isna().sum().idxmin():"UFRIC_st", \
                              df[ZL].isna().sum().idxmin():"ZL_st",\
                              df[RH].isna().sum().idxmin():"RH_st",\
                              df[WS].isna().sum().idxmin():"WS_st",\
                              df[PA].isna().sum().idxmin():"PA_st",\
                              df[TA].isna().sum().idxmin():"TA_st",\
                              df[MO_L].isna().sum().idxmin():"MO_L_st"})
        # print(df[Ufric].isna().sum().idxmin())
    elif len(RH)==0:
        df=df.rename(columns={df[Ufric].isna().sum().idxmin():"UFRIC_st", \
                        df[ZL].isna().sum().idxmin():"ZL_st",\
                        df[MO_L].isna().sum().idxmin():"MO_L_st",\
                        df[WS].isna().sum().idxmin():"WS_st",\
                        df[PA].isna().sum().idxmin():"PA_st",\
                        df[TA].isna().sum().idxmin():"TA_st"})
    else:
        df=df.rename(columns={df[Ufric].isna().sum().idxmin():"UFRIC_st", \
                              df[ZL].isna().sum().idxmin():"ZL_st",\
                              df[RH].isna().sum().idxmin():"RH_st",\
                              df[WS].isna().sum().idxmin():"WS_st",\
                              df[PA].isna().sum().idxmin():"PA_st",\
                              df[TA].isna().sum().idxmin():"TA_st"})


    return df


def merge_inst_sebal(flux_data,sebal_data,filename_flux,filename_sebal,out_dir):
    """
    Merge during landsat overpass 
    """
    merged_list=[]
    for index1 in range(len(sebal_data)):
        for index2 in range(len(flux_data)):
            # print(index2)

            if filename_sebal[index1]==filename_flux[index2]:
                # print(filename_flux[index2])
                sebal_data[index1]["date"]=pd.to_datetime(sebal_data[index1]["date"],format='ISO8601')
                sebal_data[index1]["Datetime_Local_sebal"]=sebal_data[index1]["date"].dt.tz_localize("GMT", nonexistent='shift_forward',ambiguous=False)
                sebal_data[index1]["Datetime_GMT"]=sebal_data[index1]["Datetime_Local_sebal"].dt.round("H")
                df_merge=pd.merge(sebal_data[index1],flux_data[index2],on="Datetime_GMT",how="left")
                df_merge["Name"]=filename_flux[index2]
                # print(df_merge)
                # main_list[main_list_index]["Dae"]=pd.to_datetime(main_list[main_list_index]["TIMESTAMP_START"])
                merged_list.append(df_merge)
                df_merge.to_csv(out_dir+df_merge["Name"].iloc[0]+".csv")
    return merged_list


bif_files,bif_filenames=read_bif(dir_bif)
flux_files,flux_filenames=read_flux(dir_flux)
data_insitu=[column_names_flux(file) for file in flux_files]
data_insitu=add_state(flux_files,bif_files,flux_filenames,bif_filenames)
data_insitu=[convert_timezone_gmt(file,file["State"].iloc[0]) for file in data_insitu]
# data_sebal,sebal_filenames=read_sebal(dir_sebal) # Concatenating the sebal outputs
data_sebal,sebal_filenames=read_sebal(out_dir_sebal)
data_sebal=[column_names_sebal(file) for file in data_sebal]
merged_dir="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_merged\\"
merged_files=merge_inst_sebal(data_insitu,data_sebal,flux_filenames,sebal_filenames,merged_dir)


#%%

#%%
[i.columns.tolist() for i in merged_files if i["Name"].iloc[0]=="US-Var"]
#%%
for i in range(len(flux_files)):
    print(i)
    # print(merged_files[i]["MO_LENGTH"])
    column_names_flux(flux_files[i])
# merged_files[2].columns.tolist()
# column_names_flux(flux_files[26])
# flux_files[26].columns.tolist()
#%%
for i in range(len(merged_files)):
    print(merged_files[i].shape)
merged_files[0]
# %%
