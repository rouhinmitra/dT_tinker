#%% 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import os
#%% 
## Calculate dT and group landsat scenes based on id to get spatial dT values
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
        file_name.append(flux_list[index].split(".")[0])

    return temp,file_name


def calculate_dt(df):
    """
    Calculating dT using some paper (find out the reference paper)
    For H values we remove any H<0 and do not accoubt for advection 
    """
    df["rho"]=(-0.0046 *(df["TA_st"]+273.15) ) + 2.5538
    # df = df.dropna(subset=["ZL_st"])
    df=df[df["H_inst_af"]>=0]
    if "MO_L_st" not in df.columns:
        df["es"]=0.6108*np.exp((17.27*df["TA_st"])/(df["Ta_st"]+237.3))
        df["ea"]=df["es"]*df["RH_st"]/100
        df["mr"]=0.622*(df["ea"]/(df["PA_st"]-df["ea"]))
        df["Tv"] = (1 + 0.61*df["mr"])*(df["TA_st"]+273.15)
        df["MO_L_st"]=-(df["rho"]*1004*(df["Tv"])*df["UFRIC_st"]**3)/(0.41*9.81*df["H_inst_af"])
        df['phi_v'] = df.apply(lambda row: (1-(16*(2-0.67)/row["MO_L_st"]))**(-0.5) if row["ZL_st"] < 0 else (1+(5.2*(2-0.67)/row["MO_L_st"])),axis=1)
        df["phi_m"]= df.apply(lambda row: row["phi_v"]**(0.5) if row["ZL_st"] < 0 else row["phi_v"],axis=1)
        df["rahobs"]=(df["phi_v"]/df["phi_m"])*(df["WS_st"]/(df["UFRIC_st"]**2))+(6.26*(df["UFRIC_st"]**(-2/3)))
        df["dT_obs"]=df["H_inst_af"]*df["rah"]/(1004*df["rho"])
        print("False")
    else:
        df['phi_v'] = df.apply(lambda row: (1-(16*(2-0.67)/row["MO_L_st"]))**(-0.5) if row["ZL_st"] < 0 else (1+(5.2*(2-0.67)/row["MO_L_st"])),axis=1)
        df["phi_m"]= df.apply(lambda row: row["phi_v"]**(0.5) if row["ZL_st"] < 0 else row["phi_v"],axis=1)
        df["rahobs"]=(df["phi_v"]/df["phi_m"])*(df["WS_st"]/(df["UFRIC_st"]**2))+(6.26*(df["UFRIC_st"]**(-2/3)))
        df["dT_obs"]=df["H_inst_af"]*df["rahobs"]/(1004*df["rho"])
        print("True")
    # df["H_calc"]=df["rho"]*1004*df["dT_obs"]/(df["rah"]*2)
    return df



def get_spatial_dT(list_of_files,out_dir):
    """
    Get landsat scenes covering multiple flux stations for dT analysis. 
    Concatenate all the data and groupby unique landsat id 
    Only groups with more than 1 point will be chosen for analysis
    (Don't expect any group to have more than 4)
    dTobs:dT measured
    dT:SEBAL dT 
    """
    all_points=pd.concat(list_of_files)
    all_points=all_points[(all_points["dT_obs"].notna()) & (all_points["dT"].notna())]
    all_points=all_points[all_points["dT_obs"]>=0]
    all_points=all_points[all_points["rah"]<=500]

    all_points["rah"].hist()
    print(all_points.shape)
    grouped_list=[]
    for i, g in all_points.groupby(["id"]):
        if g.shape[0]>1:
            grouped_list.append(g)
            g.to_csv(out_dir+g["id"].iloc[0]+".csv")
    # grouped_data=all_points.groupby("id")

    return grouped_list


#%% Calling functions 
merged_dir="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_merged\\"
station_list,station_names=read_files(merged_dir)
station_list=[calculate_dt(file) for file in station_list]
export_dir="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_spatialdata\\"
temp=get_spatial_dT(station_list,export_dir)

#%% Checking no of points in each station
station_list[23]["dT_obs"].hist(bins=100)
for i in station_list:
    if i.shape[0]!=0:
        print(i[(i["dT_obs"].notna()) & (i["dT"].notna())].shape)
        print(i.Name.iloc[0])
# %%
station_list[0].columns.tolist()
temp[700][["id",'latitude.1','longitude.1',"dT_obs","dT","T_LST_DEM","hot_pixel_temp","rah","rahobs","constant","constant_1","Veg"]]