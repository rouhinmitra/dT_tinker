#%%
import os 
import numpy as np 
import pandas as pd
import pytz
import datetime

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
                main_list[main_list_index]["Veg"]=metadata_list[metadata_index][metadata_list[metadata_index]["VARIABLE_GROUP"]=="GRP_IGBP"]["DATAVALUE"].iloc[0]
                # main_list[main_list_index]["Climate"]=metadata_list[metadata_index][metadata_list[metadata_index]["VARIABLE"]=="CLIMATE_KOEPPEN"]["DATAVALUE"].iloc[0]
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
    G=sorted([col for col in df.columns if "G"==col.split("_")[0]],key=len)
    rn=sorted([col for col in df.columns if "NETRAD"==col.split("_")[0]],key=len)
    
    print(G)
    print(rn)
    # Choose the most occuring variables except  for H,LE,G where we choose the first one from a list 
    if (len(LE)!=0) & (len(G)!=0) & (len(G)!=0) & (len(rn)!=0):
        df=df.rename(columns={LE[0]:"LE_inst_af",H[0]:"H_inst_af",G[0]:"G_inst_af",rn[0]:"Rn_inst_af"})
    return df

def calc_daily_Et(df):
    """ 
    Function to calcualte daily ET for only days when LEinst missing data is greater less than 10 points
    """
    # df["EBR"]=(df["LE_inst_af"]+df["H_inst_af"])/(df["Rn_inst_af"]-df["G_inst_af"])
    # print(df["EBR"].describe())
    df["Date_daily"]=pd.to_datetime(df["Datetime"].dt.date)
    var_cleaned = []
    # Replace -9999.0 with NaN in the relevant columns before the loop
    df.loc[:, "LE_inst_af"] = df["LE_inst_af"].replace(-9999.0, np.nan)
    df.loc[:, "Rn_inst_af"] = df["Rn_inst_af"].replace(-9999.0, np.nan)
    df.loc[:, "H_inst_af"] = df["H_inst_af"].replace(-9999.0, np.nan)
    df.loc[:, "G_inst_af"] = df["G_inst_af"].replace(-9999.0, np.nan)

    # Iterate over unique dates in the DataFrame
    for j in range(len(df["Date_daily"].unique())):
        # Filter DataFrame by the current unique date
        date_mask = df["Date_daily"] == df["Date_daily"].unique()[j]
        df_date = df[date_mask]

        # Check if the number of NaNs in 'LE_inst_af' is less than 10
        if df_date["LE_inst_af"].isna().sum() < 10:
            print(j)
            tmp = df_date.copy()  # Create a copy to avoid setting values on a view

            # Add new columns with counts of NaNs for each relevant variable
            tmp.loc[:, "LE_na"] = tmp["LE_inst_af"].isna().sum()
            tmp.loc[:, "Rn_na"] = tmp["Rn_inst_af"].isna().sum()
            tmp.loc[:, "h_na"] = tmp["H_inst_af"].isna().sum()
            tmp.loc[:, "g_na"] = tmp["G_inst_af"].isna().sum()

            # Append the cleaned DataFrame to the list
            var_cleaned.append(tmp)
            # print(df["Date_daily"].unique()[j])
    if len(var_cleaned)!=0:
        var_new=pd.concat(var_cleaned) # Concatenate the list to a table 
        df_daily=var_new[["Date_daily","LE_inst_af", \
                    "Rn_inst_af","H_inst_af","G_inst_af","LE_na","Rn_na",\
                        "h_na","g_na"]].groupby(["Date_daily"]).mean().reset_index()
        df_daily["Name"]=df["Name"].iloc[0]

    return df_daily

def calculate_EBR(df_daily):
    """
    Calculate Bowen ratio and remotve outliers
    """
    print(df_daily.shape[0])
    df_daily["EBR"]=(df_daily["LE_inst_af"]+df_daily["H_inst_af"])/(df_daily["Rn_inst_af"]-df_daily["G_inst_af"])
    q3, q1 = df_daily["EBR"].describe()[6],df_daily["EBR"].describe()[4]
    # print("Shape of the daily dataframe",df_daily.shape[0])
    iqr = q3 - q1
    lb=q1-1.5*iqr
    ub=q3+1.5*iqr
    df_daily=df_daily[(df_daily["EBR"]>=lb) & (df_daily["EBR"]<=ub)]

    return df_daily

def fill_ebr_gaps(ebr_series):
    """
    get daily data and calucalte a consitent bowen ratio to get closed LE 
    """
    filled_ebr_series = ebr_series.copy().reset_index()
    print(ebr_series)
    filled_ebr_series["EBR_cor"]=np.nan
    for i in range(len(ebr_series)):
        # Step 4: Sliding window of +/- 7 days (15 days)
        window_start = ebr_series.Date_daily.iloc[i]-datetime.timedelta(days=7)
        window_end = ebr_series.Date_daily.iloc[i]+datetime.timedelta(days=8)  # +8 to include the current day

        window_values = ebr_series[(ebr_series.Date_daily>=window_start) & (ebr_series.Date_daily<=window_end)]
        print(len(window_values),i)
        # Step 5: If less than +/- 5 days exist, use mean EBR of +/- 5 day sliding window
        if len(window_values)>=11:
            inverse_ebr = 1 / window_values["EBR"].describe().iloc[5]
            # print(inverse_ebr)
            print(inverse_ebr * ebr_series["LE_inst_af"].iloc[i])
            if ((inverse_ebr * ebr_series["LE_inst_af"].iloc[i]) > 850) or ((inverse_ebr * ebr_series["LE_inst_af"].iloc[i]) < -100):
                print("lets go")
                filled_ebr_series.iloc[i,filled_ebr_series.columns.get_loc('EBR_cor')]=np.nan
            else:
                # print("EBR median",window_values["EBR"].describe().iloc[5])
                # print("EBR new",window_values["EBR"].describe().iloc[5] )
                filled_ebr_series.iloc[i,filled_ebr_series.columns.get_loc('EBR_cor')]=window_values["EBR"].describe().iloc[5]
                # filled_ebr_series.at[i,'EBR_cor']=window_values["EBR"].describe().iloc[5]
                # print("Value added", window_values["EBR"].describe().iloc[5])
                # print("value shown", filled_ebr_series.iloc[i,filled_ebr_series.columns.get_loc('EBR_cor')])
        elif len(window_values)<11:
            mean_ebr = window_values.EBR.mean()
            inverse_ebr = 1 / mean_ebr
            # print(inverse_ebr)
            print(inverse_ebr * ebr_series["LE_inst_af"].iloc[i])
            if ((inverse_ebr * ebr_series["LE_inst_af"].iloc[i]) > 850) or ((inverse_ebr * ebr_series["LE_inst_af"].iloc[i]) < -100):
                print("lets go")
                filled_ebr_series.iloc[i,filled_ebr_series.columns.get_loc('EBR_cor')]=np.nan
            else: 
                filled_ebr_series.iloc[i,filled_ebr_series.columns.get_loc('EBR_cor')]=mean_ebr
        else: ## Probably need to add climatology in the future 
            filled_ebr_series.iloc[i,filled_ebr_series.columns.get_loc('EBR_cor')]=np.nan
    return filled_ebr_series

def calculate_LE_closed(df):
    """ Calculate LE closed """
    df["Residual_unclosed"]=df["Rn_inst_af"]-df["G_inst_af"]-df["LE_inst_af"]-df["H_inst_af"]
    df["LE_closed"]=df["LE_inst_af"]/df["EBR_cor"]
    df["H_closed"]=df["H_inst_af"]/df["EBR_cor"]
    df["Residual_closed"]=df["Rn_inst_af"]-df["G_inst_af"]-df["LE_closed"]-df["H_closed"]
    df["LE_unclosed"]=df["LE_inst_af"]
    df["H_unclosed"]=df["H_inst_af"]
    df["G_unclosed"]=df["G_inst_af"]
    df["Rn_unclosed"]=df["Rn_inst_af"]
    df=df[(df["Rn_inst_af"]>=10) & (df["Rn_inst_af"]<=400)]
    return df

def merge_inst_and_daily_insitu(df_daily,df_inst):
    """Merging the daily data with instantaneous data
    Assuming that the two dataframes are of the same station
    """
    df=pd.merge(df_daily[["Date_daily","LE_closed","LE_unclosed",\
                          "H_closed","H_unclosed","G_unclosed","Rn_unclosed",\
                           "Residual_unclosed","Residual_closed" ]], df_inst,on="Date_daily",how="left")

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
                # df_merge.to_csv(out_dir+df_merge["Name"].iloc[0]+".csv")
    return merged_list
#%%
bif_files,bif_filenames=read_bif(dir_bif)
flux_files,flux_filenames=read_flux(dir_flux)
data_insitu=[column_names_flux(file) for file in flux_files]
data_insitu=add_state(data_insitu,bif_files,flux_filenames,bif_filenames)
data_insitu=[convert_timezone_gmt(file,file["State"].iloc[0]) for file in data_insitu]
required_columns = {"Rn_inst_af", "G_inst_af", "LE_inst_af", "H_inst_af"}
# Filter the dataframes
data_insitu_allflux = [df for df in data_insitu if required_columns.issubset(df.columns)]
#%%
filtered_flux_filenames=[df["Name"].iloc[0] for df in data_insitu_allflux]
daily_list=[calc_daily_Et(df) for df in data_insitu_allflux]
daily_list=[calculate_EBR(df) for df in daily_list]
daily_list=[fill_ebr_gaps(df) for df in daily_list]
daily_list=[calculate_LE_closed(df) for df in daily_list]
daily_inst_insitu=[merge_inst_and_daily_insitu(daily_list[index],data_insitu_allflux[index]) for index in range(len(data_insitu_allflux))]
data_sebal,sebal_filenames=read_sebal(out_dir_sebal)
data_sebal=[column_names_sebal(file) for file in data_sebal]
merged_dir="D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\ML\\dT_data\\"
merged_files=merge_inst_sebal(daily_inst_insitu,data_sebal,filtered_flux_filenames,sebal_filenames,merged_dir)
# %%
print(daily_list[6].describe())
# calc_daily_Et(data_insitu_allflux[0])
daily_list[0]
fill_ebr_gaps(daily_list[0])
# %%
daily_list[0]
# daily_list=[fill_ebr_gaps(df) for df in daily_list]
len(daily_list)
# %%
daily_list[0]
