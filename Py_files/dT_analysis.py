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
Experiments to analyze the slope and constant of dT=aTs+b equation 
1. Can it improve Hinst and LEinst 
2. If not how? 

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

def downstream_calculations(df,dT_colname,mode):
    """
    Calculating new H and LE values that arise from regressed dT values 
    with rah being multiplied by 2 
    """
    df["rho_model"]=df["Hinst"]*df["rah"]/(df["dT"]*1004)
    df["H_"+str(mode)]=df["rho_model"]*1004*df[dT_colname]/(df["rah"]*2) 
    df["LE_"+str(mode)]=df["Rn"]-df["Ginst"]-df["H_"+str(mode)]
    # print(df["H_coldpixelregress"])
    return df

def regression_fixedcoldpixel(df):
    """
    Fix the dT=0 for the selected cold pixel as a point and find slope and intercept
    using 3+ points
    """
    # Add the cold pixel temp and dT as a row to the dataframe
    new_row = {col: np.nan for col in df.columns}
    new_row['T_LST_DEM'] = df.cold_pixel_temp.iloc[0]
    new_row['dT_obs']=0
    new_row_df = pd.DataFrame(new_row, index=[0])
    # Append the new row to the existing DataFrame
    df = pd.concat([df, new_row_df], ignore_index=True)
    print(df[["dT_obs","dT","T_LST_DEM","constant"]])

    #Run regression passing through cold pixel 
    # Extract the first point (A1, B1)
    ts_cold, dt_cold = df["T_LST_DEM"].iloc[-1], df["dT_obs"].iloc[-1]
    # Transform the data so the first point is at the origin
    ts_transformed = df['T_LST_DEM'] - ts_cold
    dt_transformed = df['dT_obs'] - dt_cold

    # Fit the line y = mx to the transformed data (excluding the first point)
    model = LinearRegression(fit_intercept=False)  # No intercept, line passes through the origin
    model.fit(ts_transformed[1:].values.reshape(-1, 1), dt_transformed[1:].values)

    # Calculate the slope (m) and the intercept (b)
    m = model.coef_[0]
    b = dt_cold - m * ts_cold
    df["m_coldpixelregress"]=m
    df["b_coldpixelregress"]=b
    # Define the fitted line
    def fitted_line(x):
        return m * x + b
    df["dT_coldpixelregress"]=fitted_line(df['T_LST_DEM'])
    df=downstream_calculations(df,"dT_coldpixelregress","coldpixelregress")
    # # Print the slope and intercept
    print(f"Slope (m): {m}")
    print(f"Intercept (b): {b}")

    # # # Plot the data and the fitted line
    # plt.scatter(df['T_LST_DEM'], df['dT_obs'], label='Data points')
    # plt.plot(df['T_LST_DEM'], fitted_line(df['T_LST_DEM']), color='red', label=f'Fitted line: y = {m:.2f}x + {b:.2f}')
    # plt.plot(df["T_LST_DEM"],45-45*np.exp(-(df["T_LST_DEM"]-298)/120),c="r")
    # plt.xlabel('A')
    # plt.ylabel('B')
    # plt.legend()
    # plt.title('Line fit through the first point')
    # plt.show()

    return df

def regression_all(df):
    """
    Instead of keeping an anchor pixel we fit a general regression line
    """
    # Fit the line y = mx to the transformed data (excluding the first point)
    model = LinearRegression(fit_intercept=True)  # No intercept, line passes through the origin
    model.fit(df["T_LST_DEM"].values.reshape(-1, 1), df["dT_obs"].values)
    print(model.coef_[0],model.intercept_)
    m=model.coef_[0]
    b=model.intercept_
    df["m_allregress"]=model.coef_[0]
    df["b_allregress"]=model.intercept_
    # Define the fitted line
    def fitted_line(x):
        return m * x + b
    df["dT_allregress"]=fitted_line(df['T_LST_DEM'])
    df=downstream_calculations(df,"dT_allregress","allregress")

    return df


def regression_exp(df):
    df["rho_model"]=df["Hinst"]*df["rah"]/(df["dT"]*1004)
    df["hot_pixel_dT"]=(df["Rn"]-df["Ginst"])*df["rah"]/(1004*df["rho_model"])
    b=(df["hot_pixel_temp"]-df["cold_pixel_temp"])/np.log(df["hot_pixel_dT"]+1)
    df["dT_exp"]=np.exp(-(df["cold_pixel_temp"]-df["T_LST_DEM"])/b)-1
    df=downstream_calculations(df,"dT_exp","exp")
    print(df["LE_exp"])
    return df

def MAPE(Y_actual,Y_Predicted):
    mape = np.mean(( Y_Predicted-Y_actual))*100/np.mean(Y_actual)
    return mape

def rmse(Y_actual,Y_Predicted): #in W/m2
    return mean_squared_error(Y_actual,Y_Predicted,squared=False)

def error_analysis_by_lancover(list_of_files,suffix):
    """
    Make scatter plots of measured LEinst af wrt LE sebal and LE cold pixel regress 
    Also make scatter plot of slope of SEBAL vs slope of modified sebal
    Suffix: type of dT modification
    """
    concatenated_df = pd.concat(list_of_files, ignore_index=True)
    print("No of negative values of LEinst in sebal orig",concatenated_df[concatenated_df["LEinst"]<0].shape[0])
    print("No of negative values of LEinst in sebal dt mod",concatenated_df[concatenated_df["LE_"+str(suffix)]<0].shape[0])

    concatenated_df=concatenated_df[(concatenated_df["LEinst"]>=0) & (concatenated_df["LE_"+str(suffix)]>=0) \
         & (concatenated_df["LE_inst_af"]>=0)]

    # Step 2: Group by the "veg" column
    grouped = concatenated_df.groupby('Veg')
    # Step 3: Create scatter plots for each "veg" category
    for veg_category, group in grouped:
        plt.figure()
        plt.scatter(group['LE_inst_af'], group['LEinst'],c="r",label="SEBAL orig")
        plt.scatter(group['LE_inst_af'], group["LE_"+str(suffix)],c="b",label="SEBAL dTmod")  # Replace 'x' and 'y' with your actual column names for the scatter plot
        plt.scatter(group['LE_inst_af'],group["Rn"]-group["Ginst"]-group["H_inst_af"],c="g",label="SEBAL Hinsitu")  

        plt.plot(np.arange(0,600,5),np.arange(0,600,5))
        plt.title(f'Scatter Plot for veg = {veg_category}')
        plt.xlabel('LE measured')  # Replace with your actual label
        plt.ylabel('LE model')  # Replace with your actual label
        plt.annotate(f' RMSE: {rmse(group["LE_inst_af"], group["LEinst"]):.2f}%',
             xy=(0.95, 0.1), xycoords='axes fraction',
             ha='right', va='bottom',
             fontsize=15, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        plt.annotate(f' RMSE mod : {rmse(group["LE_inst_af"], group["LE_"+str(suffix)]):.2f}%',
             xy=(0.95, 0.2), xycoords='axes fraction',
             ha='right', va='bottom',
             fontsize=15, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        plt.legend()
        plt.show()
        plt.figure()
        plt.scatter(group['H_inst_af'], group['Hinst'],c="r",label="SEBAL orig")
        plt.scatter(group['H_inst_af'], group['H_'+str(suffix)],c="b",label="SEBAL dTmod")  # Replace 'x' and 'y' with your actual column names for the scatter plot
        plt.plot(np.arange(0,500,1),np.arange(0,500,1))

        plt.title(f'Scatter Plot for veg = {veg_category}')
        plt.xlabel('H measured')  # Replace with your actual label
        plt.ylabel('H model')  # Replace with your actual label
        plt.legend()
        plt.show()
        plt.figure()
        cm = plt.cm.get_cmap('RdYlBu')
        xy = group["LAI"]
        z = xy
        sc = plt.scatter(group["rahobs"], group["rah"], c=z, vmin=0, vmax=3, s=35, cmap=cm)
        # plt.scatter(group["rahobs"], group["rah_first"], c="g")

        plt.plot(np.arange(0,50,10), np.arange(0,50,10), linestyle='--', color='gray', label='1:1 Line')

        plt.colorbar(sc,label="LAI")
        plt.xlabel("rah obs")
        plt.ylabel("rah model")
        plt.title(f'Scatter Plot for veg = {veg_category}')
        plt.xlabel('rah measured')  # Replace with your actual label
        plt.ylabel('rah estimated')  # Replace with your actual label
        plt.legend()
        plt.show()
        ## Friction velocity
        plt.figure()
        plt.scatter(group['UFRIC_st'], group['u_fr_1'],c="r",label="U star initial")
        plt.scatter(group['UFRIC_st'], group['ufric_star'],c="b",label="U star final")  # Replace 'x' and 'y' with your actual column names for the scatter plot
        plt.plot(np.arange(0,3,1),np.arange(0,3,1))

        plt.title(f'Scatter Plot for veg = {veg_category}')
        plt.xlabel('u star measured')  # Replace with your actual label
        plt.ylabel('u star model')  # Replace with your actual label
        plt.legend()
        plt.show()
        group["rah_error"]=group["rah"]-group["rahobs"]
        corr_matrix=group[["rah_error","rahobs","NDVI_model","T_LST_DEM","LAI","WS_st","TA_st","MO_L_st","ZL_st"]]
        sns.heatmap(corr_matrix.corr());
        print("rah vs LST",group["rahobs"].corr(group["T_LST_DEM"]))
        print("rah vs WS",group["rahobs"].corr(group["WS_st"]))
        print("rah vs LAI",group["rahobs"].corr(group["LAI"]))
        print("rah vs Z/L",group["rahobs"].corr(group["ZL_st"]))
        plt.figure()

        plt.plot(group["ZL_st"],group["rahobs"],"o")
        plt.show()

    return 
  
def error_analysis_by_station(list_of_files,suffix):
    """
    Make scatter plots of measured LEinst af wrt LE sebal and LE cold pixel regress 
    Also make scatter plot of slope of SEBAL vs slope of modified sebal
    Suffix: type of dT modification
    """
    concatenated_df = pd.concat(list_of_files, ignore_index=True)
    print("No of negative values of LEinst in sebal orig",concatenated_df[concatenated_df["LEinst"]<0].shape[0])
    print("No of negative values of LEinst in sebal dt mod",concatenated_df[concatenated_df["LE_"+str(suffix)]<0].shape[0])

    concatenated_df=concatenated_df[(concatenated_df["LEinst"]>=0) & (concatenated_df["LE_"+str(suffix)]>=0) \
         & (concatenated_df["LE_inst_af"]>=0)]

    # Step 2: Group by the "veg" column
    grouped = concatenated_df.groupby('Name')
    # Step 3: Create scatter plots for each "veg" category
    for name, group in grouped:
        plt.figure()
        plt.scatter(group['LE_inst_af'], group['LEinst'],c="r",label="SEBAL orig")
        plt.scatter(group['LE_inst_af'], group["LE_"+str(suffix)],c="b",label="SEBAL dTmod")  # Replace 'x' and 'y' with your actual column names for the scatter plot
        plt.scatter(group['LE_inst_af'],group["Rn"]-group["Ginst"]-group["H_inst_af"],c="g",label="SEBAL Hinsitu")  

        plt.plot(np.arange(0,600,5),np.arange(0,600,5))
        plt.title(f'Scatter Plot for veg = {name}')
        plt.xlabel('LE measured')  # Replace with your actual label
        plt.ylabel('LE model')  # Replace with your actual label
        plt.annotate(f' RMSE: {rmse(group["LE_inst_af"], group["LEinst"]):.2f}%',
             xy=(0.95, 0.1), xycoords='axes fraction',
             ha='right', va='bottom',
             fontsize=15, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        plt.annotate(f' RMSE mod : {rmse(group["LE_inst_af"], group["LE_"+str(suffix)]):.2f}%',
             xy=(0.95, 0.2), xycoords='axes fraction',
             ha='right', va='bottom',
             fontsize=15, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        plt.legend()
        plt.show()
        plt.figure()
        plt.scatter(group['H_inst_af'], group['Hinst'],c="r",label="SEBAL orig")
        plt.scatter(group['H_inst_af'], group['H_'+str(suffix)],c="b",label="SEBAL dTmod")  # Replace 'x' and 'y' with your actual column names for the scatter plot
        plt.plot(np.arange(0,500,1),np.arange(0,500,1))

        plt.title(f'Scatter Plot for veg = {name}')
        plt.xlabel('H measured')  # Replace with your actual label
        plt.ylabel('H model')  # Replace with your actual label
        plt.legend()
        plt.show()
        plt.figure()
        cm = plt.cm.get_cmap('RdYlBu')
        xy = group["LAI"]
        z = xy
        sc = plt.scatter(group["rahobs"], group["rah"], c=z, vmin=0, vmax=3, s=35, cmap=cm)

        plt.plot(np.arange(0,50,10), np.arange(0,50,10), linestyle='--', color='gray', label='1:1 Line')

        plt.colorbar(sc,label="LAI")
        plt.xlabel("rah obs")
        plt.ylabel("rah model")
        # plt.title(str(index))
        # plt.show()

        # plt.scatter(group['dT_obs'], group['dT_coldpixelregress'],c="b",label="SEBAL dTmod")  # Replace 'x' and 'y' with your actual column names for the scatter plot
        # plt.plot(np.arange(0,20,1),np.arange(0,20,1))

        plt.title(f'Scatter Plot for veg = {name}')
        plt.xlabel('rah measured')  # Replace with your actual label
        plt.ylabel('rah estimated')  # Replace with your actual label
        plt.legend()
        plt.show()

    return 

#%%
dir="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_spatialdata\\"
dt_data=read_files(dir)
dt_cold=[regression_fixedcoldpixel(df) for df in dt_data]
# dt_exp=[regression_exp(df) for df in dt_data]

# %%
a=regression_fixedcoldpixel(dt_data[650])
a[["Name","dT_obs","dT","dT_coldpixelregress","Hinst","H_coldpixelregress","H_inst_af","LEinst","LE_coldpixelregress","LE_inst_af","rah","rahobs","Rn","NETRAD","constant","m_coldpixelregress","Veg"]]
a=regression_all(dt_data[560])
a[["Name","dT_obs","dT","dT_allregress","Hinst","H_allregress","H_inst_af","LEinst","LE_allregress","LE_inst_af","rah","rahobs","Rn","NETRAD","constant","m_allregress","Veg"]]
a=regression_exp(dt_data[0])
a[["Name","dT_obs","dT","dT_exp","T_LST_DEM","hot_pixel_temp","Hinst","H_exp","H_inst_af","LEinst","LE_exp","LE_inst_af","rah","rahobs","Rn","NETRAD","constant","Veg"]]

#%%
error_analysis_by_lancover(dt_cold,"coldpixelregress")
# error_analysis_by_station(dt_cold,"coldpixelregress")
# error_analysis_by_lancover(dt_exp,"exp")
# dt_calculate[0]
# %%
dt_data[0].columns.tolist()
