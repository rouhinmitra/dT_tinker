#%%
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os 
#%%
os.chdir("D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\Csv_Files\\Merge_inst_sebal_daily")
dT_list=[]
file_list=os.listdir()
for index in range(len(file_list)):
    tmp=pd.read_csv(file_list[index])
    if set(['USTAR','ZL']).issubset(tmp.columns):
        if tmp.shape[0]!=0:
            print(tmp.shape[0])
            dT_list.append(tmp)
for index in range(len(dT_list)):
    dT_list[index]["Name"]=dT_list[index]["Name_x"]
    dT_list[index]=dT_list[index].drop(columns={'Unnamed: 0.2','Name_x',"Name_y","date","Unnamed: 0_y","Unnamed: 0_x"})
    dT_list[index]["Date"]=pd.to_datetime(dT_list[index]["Date"])
# We run the function to calculate rah and dT obs 
def calculate_dt(df,h_col,ta_col,ws_col,length=False):
    if "TA_1_1_1" in df.columns and "PA_1_1_1" in df.columns :
        df["TA"]=df["TA_1_1_1"]
        df["PA"]=df["PA_1_1_1"]
    elif "TA_PI_F" in df.columns:
        df["TA"]=df["TA_PI_F"]
    elif "TA_1_1_1" in df.columns:
        df["TA"]=df["TA_1_1_1"]
    elif "NDVI_x" in df.columns:
        df["NDVI"]=df["NDVI_x"]
        df["NDVI_st"]=df["NDVI_y"]
       

    df["rho"]=(-0.0046 *(df[ta_col]+273.15) ) + 2.5538
    df["mr"]=0.622*(df["ea"]/(df["PA"]-df["ea"]))
    df["Tv"] = (1 + 0.61*df["mr"])*(df["TA"]+273.15)
    df["mo_l"]=-(df["rho"]*1004*(df["Tv"])*df["USTAR"]**3)/(0.41*9.81*df[h_col])
    # df = df.dropna(subset=['ZL'])

    if length==False:
        df['phi_v'] = df.apply(lambda row: (1-(16*(2-0.67)/row["mo_l"]))**(-0.5) if row['ZL'] < 0 else (1+(5.2*(2-0.67)/row["mo_l"])),axis=1)
        df["phi_m"]= df.apply(lambda row: row["phi_v"]**(0.5) if row['ZL'] < 0 else row["phi_v"],axis=1)
        df["rahobs"]=(df["phi_v"]/df["phi_m"])*(df[ws_col]/(df["USTAR"]**2))+(6.26*(df["USTAR"]**(-2/3)))
        df["dT_obs"]=df[h_col]*df["rah"]/(1004*df["rho"])
        print("False")
    else:
        df['phi_v'] = df.apply(lambda row: (1-(16*(2-0.67)/row["MO_LENGTH"]))**(-0.5) if row['ZL'] < 0 else (1+(5.2*(2-0.67)/row["mo_l"])),axis=1)
        df["phi_m"]= df.apply(lambda row: row["phi_v"]**(0.5) if row['ZL'] < 0 else row["phi_v"],axis=1)
        df["rahobs"]=(df["phi_v"]/df["phi_m"])*(df[ws_col]/(df["USTAR"]**2))+(6.26*(df["USTAR"]**(-2/3)))
        df["dT_obs"]=df[h_col]*df["rahobs"]/(1004*df["rho"])
        print("True")
    df["rho_model"]=df["Hinst"]*df["rah"]/(df["dT"]*1004)
    df["H_calc"]=df["rho_model"]*1004*df["dT_obs"]/(df["rah"]*2)
    return df


for index in range(len(dT_list)):
    print(index)
    if "MO_LENGTH" in dT_list[index].columns:
        dT_list[index]=calculate_dt(dT_list[index],"H_inst_af","TA","WS",True)
    else:
        dT_list[index]=calculate_dt(dT_list[index],"H_inst_af","TA","WS")
print(dT_list[0].columns.tolist())
# %%
## Get errors 
### Calculate errors in rah and dT 
from sklearn.metrics import mean_squared_error
def bias_points(df,y,x,new_col):
    df[new_col]=(df[y]-df[x])/df[x]
    return df
def abs_points(df,y,x,new_col):
    df[new_col]=(df[y]-df[x]).abs()/df[x].abs()
    return df
## Bias 

for index in range(len(dT_list)):
    # print(index)
    dT_list[index]=bias_points(dT_list[index],"rah","rahobs","bias_rah")
    dT_list[index]=bias_points(dT_list[index],"dT","dT_obs","bias_dT")
    dT_list[index]=bias_points(dT_list[index],"Hinst","H_inst_af","bias_H")
    dT_list[index]=bias_points(dT_list[index],"LEinst","LE_inst_af","bias_H")
    dT_list[index]=bias_points(dT_list[index],"ux_G","WS","bias_u")

##MAE 
    dT_list[index]=abs_points(dT_list[index],"rah","rahobs","mae_rah")
    dT_list[index]=abs_points(dT_list[index],"dT","dT_obs","mae_dT")
    dT_list[index]=abs_points(dT_list[index],"Hinst","H_inst_af","mae_H")
    dT_list[index]=abs_points(dT_list[index],"LEinst","LE_inst_af","mae_H")
    dT_list[index]=abs_points(dT_list[index],"ux_G","WS","mae_u")


#%% Plot 3d plots 
def plot_cbar(df,index):
    cm = plt.cm.get_cmap('RdYlBu')
    xy = df["NDVI"]
    z = xy
    sc = plt.scatter(df["rahobs"], df["rah"], c=z, vmin=0, vmax=1, s=35, cmap=cm)

    plt.plot(np.arange(0,50,10), np.arange(0,50,10), linestyle='--', color='gray', label='1:1 Line')

    plt.colorbar(sc,label="hot pixel temp")
    plt.xlabel("rah obs")
    plt.ylabel("rah model")
    plt.title(str(index))
    plt.show()
    ## Plotting scatter plots with color bar 
    cm = plt.cm.get_cmap('RdYlBu')
    xy = df["NDVI"]
    z = xy
    sc = plt.scatter(df["H_inst_af"], df["Hinst"], c=z, vmin=0, vmax=1, s=35, cmap=cm)

    plt.plot(np.arange(0,500,10), np.arange(0,500,10), linestyle='--', color='gray', label='1:1 Line')

    plt.colorbar(sc,label="NDVI")
    plt.xlabel("H obs")
    plt.ylabel("H est")
    plt.title(str(index))
    plt.show()
    ## Plotting scatter plots with color bar 
    cm = plt.cm.get_cmap('RdYlBu')
    xy = df["NDVI"]
    z = xy
    sc = plt.scatter(df["dT_obs"], df["dT"], c=z, vmin=0.1, vmax=0.8,s=35, cmap=cm)

    plt.plot(np.arange(0,20,10), np.arange(0,20,10), linestyle='--', color='gray', label='1:1 Line')

    plt.colorbar(sc,label="NDVI")
    plt.xlabel("dT obs")
    plt.ylabel("dT est")
    plt.title(str(index))
    plt.show()
    ## Plotting scatter plots with color bar 
    cm = plt.cm.get_cmap('RdYlBu')
    xy = df["NDVI"]
    z = xy
    sc = plt.scatter(df["H_inst_af"], df["H_calc"], c=z, vmin=0, vmax=0.8,s=35, cmap=cm)

    plt.plot(np.arange(0,500,10), np.arange(0,500,10), linestyle='--', color='gray', label='1:1 Line')

    plt.colorbar(sc,label="NDVI")
    plt.xlabel("H obs")
    plt.ylabel("H est w obs dT")
    # plt.ylim(5,30)
    # plt.xlim(0,100)

    plt.title(str(index))
    plt.show()
    ## Plotting scatter plots with color bar 
    cm = plt.cm.get_cmap('RdYlBu')
    xy = df["cold_pixel_temp"]
    z = xy
    sc = plt.scatter(df["dT_obs"], df["dT"], c=z, vmin=270, vmax=300,s=35, cmap=cm)

    plt.plot(np.arange(0,20,10), np.arange(0,20,10), linestyle='--', color='gray', label='1:1 Line')

    plt.colorbar(sc,label="Hot pixel temp")
    plt.xlabel("dT obs")
    plt.ylabel("dT est")
    plt.xlim(0,20)
    plt.title(str(index))
    plt.show()
# plot_cbar(dT_list[0],dT_list[0]["Veg"].iloc[0])
# dT_list[0].columns.tolist()
for i in range(len(dT_list)):
    plot_cbar(dT_list[i],dT_list[i]["Veg"].iloc[0])
    # print(dT_list[i]["mae_dT"].corr(dT_list[i]["NDVI"]))

#%%
# Merge sentinel 1 to the dataframe 
import sys 
import os
import importlib
sys.path.append(os.path.abspath("D:\\Backup\\Rouhin_Lenovo\\US_project\\geeSEBAL_Tinker\\Py_files\\"))
import merge as mg
import Sen_ls_merge as sls
importlib.reload(mg) 
importlib.reload(sls) 

os.chdir("D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Input_Data\\Sentinel_1\\30m\\US_WUS\\")
file_list=os.listdir()
sen1_all=[]
for i in range(len(file_list)):
    sen1_all.append(pd.read_csv(file_list[i],parse_dates=["date"]))
    sen1_all[i]["Date"]=pd.to_datetime(sen1_all[i]["date"].dt.date)
    sen1_all[i]["Name"]=file_list[i].split(".")[0]
# dT_list[0]["Unnamed: 0_y"]
# def mergefromlists(main_frame,second_frame,common_col,mf_name,sf_name,how="left"):
merged_list=mg.mergefromlists(dT_list,sen1_all,"Date","Name","Name",how="outer")
print(len(merged_list),len(dT_list))
sen1ls=sls.sen1_ls_join(merged_list,2)
for i in range(len(sen1ls)):
    sen1ls[i]["VV_VH"]=sen1ls[i]["VV"]/sen1ls[i]["VH"]
# dT_list[0].columns.tolist()
#%% Plotting correlation of Sen1 with dT and or rah
def plot_radar(df,index):
    plt.scatter(df["USTAR"],df["VV_VH"],s=35)
    plt.xlabel("u fric obs")
    # plt.xlim(0,15)
    plt.ylabel("VV_VH")
    plt.title(str(index))
    plt.show()

    plt.scatter(df["USTAR"],df["VH"],s=35)
    plt.xlabel("u fric obs")
    # plt.xlim(0,15)
    plt.ylabel("VH")
    plt.title(str(index))
    plt.show()

    plt.scatter(df["rahobs"],df["VV_VH"],s=35)
    plt.xlabel("rah")
    plt.ylabel("VV_VH")
    plt.xlim(0,80)
    plt.title(str(index))
    plt.show()
    
    plt.scatter(df["rahobs"],df["VH"],s=35)
    plt.xlabel("rah")
    plt.ylabel("VH")
    plt.xlim(0,80)
    plt.title(str(index))
    plt.show()

    plt.scatter(df["H_inst_af"],df["VV_VH"],s=35)
    plt.xlabel("Hobs")
    plt.ylabel("VV_VH")
    # plt.xlim(0,125)
    plt.title(str(index))
    plt.show()
    
    plt.scatter(df["H_inst_af"],df["VH"],s=35)
    plt.xlabel("Hobs")
    plt.ylabel("VH")
    # plt.xlim(0,125)
    plt.title(str(index))
    plt.show()
for i in range(len(sen1ls)):
    plot_radar(sen1ls[i],sen1ls[i]["Veg"].iloc[0])

# %%
