#%% 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import os
from sklearn.linear_model import LinearRegression

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
    """
    df["rho_model"]=df["Hinst"]*df["rah"]/(df["dT"]*1004)
    df["H_"+str(mode)]=df["rho_model"]*1004*df[dT_colname]/df["rah"]
    df["LE_"+str(mode)]=df["Rn"]-df["Ginst"]-df["H_"+str(mode)]
    print(df["H_coldpixelregress"])

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

    # # Plot the data and the fitted line
    plt.scatter(df['T_LST_DEM'], df['dT_obs'], label='Data points')
    plt.plot(df['T_LST_DEM'], fitted_line(df['T_LST_DEM']), color='red', label=f'Fitted line: y = {m:.2f}x + {b:.2f}')
    plt.plot(df["T_LST_DEM"],45-45*np.exp(-(df["T_LST_DEM"]-298)/120),c="r")
    plt.xlabel('A')
    plt.ylabel('B')
    plt.legend()
    plt.title('Line fit through the first point')
    plt.show()

    return df

#%%
dir="D:\\Backup\\Rouhin_Lenovo\\US_project\\Untitled_Folder\\Data\\Inst_project\\dT_spatialdata\\"
dt_data=read_files(dir)

# %%
a=regression_fixedcoldpixel(dt_data[553])
a[["Name","dT_obs","dT","dT_coldpixelregress","Hinst","H_coldpixelregress","H_inst_af","LEinst","LE_coldpixelregress","LE_inst_af","rah","rahobs","Rn","Rn_inst_af","constant","m_coldpixelregress"]]
# a.columns
# %%
