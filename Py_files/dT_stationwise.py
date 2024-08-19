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


# %% Pick sample stations
for i in range(len(dt_data)):
    print(dt_data[i].shape)
    if dt_data[i].shape[0]>=100:
        print(dt_data[i].Veg.iloc[0],dt_data[i].Name.iloc[0],dt_data[i].shape[0],dt_data[i].State.iloc[0],i)
# len(dt_data)
## Choose GRA US VAR, CRO: US TW3 , CRO; US RC3, WET: US Bi1 US Myb, CSH: US-Rls, WSA: US Ton
# US UIB Cropland< OSH: US Jo1 , BSV: US ADR, 
select_stations=[]
for i in range(len(dt_data)):
    if i==1 or i==3 or i==21 or i==42 or i==29 or i==53 or i==62 or i==66 or i==39:
        select_stations.append(dt_data[i])
        # print(dt_data[i][["dT_obs","dT","rahobs"]].describe())

# %%
def plot_dT_LST_scatter(df):
    """
    Plots a scatter plot between 'dT_obs' and 'NDVI_model' with the title including station name and vegetation.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the columns 'dT_obs', 'T_LST_DEM', 'Name', and 'Veg'.
    """
     # Check if required columns exist in the dataframe
    required_columns = ['dT_obs', 'T_LST_DEM', 'Name', 'Veg']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe")
    
    # Extracting the station name and vegetation type
    station_name = df['Name'].iloc[0]
    vegetation = df['Veg'].iloc[0]
    
    # Calculating the correlation coefficient
    correlation = np.corrcoef(df['T_LST_DEM'], df['dT_obs'])[0, 1]
    
    # Creating the scatter plot with regression line
    plt.figure(figsize=(10, 6))
    sns.regplot(x='T_LST_DEM', y='dT_obs', data=df, scatter_kws={'s': 100, 'alpha': 1}, line_kws={'color': 'red'})
    # sns.regplot(x='T_LST_DEM', y='dT', data=df, scatter_kws={'s': 100, 'alpha': 1,'color': "k"}, line_kws={'color': 'red'})

    plt.title(f"Station: {station_name}, Vegetation: {vegetation}", fontsize=20)
    plt.xlabel("LST (K)", fontsize=20)
    plt.ylabel("Measured dT (C)", fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid(True)
    plt.ylim(-2,18)
    # Adding the correlation coefficient text
    plt.text(0.95, 0.85, f'r= {correlation:.2f}', 
             fontsize=25, 
             transform=plt.gca().transAxes,
             verticalalignment='bottom', 
             horizontalalignment='right')
    
    plt.show()
#-------------------------------- NDVI 
def plot_dT_NDVI_scatter(df):
    """
    Plots a scatter plot between 'dT_obs' and 'T_LST_DEM' with the title including station name and vegetation.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the columns 'dT_obs', 'T_LST_DEM', 'Name', and 'Veg'.
    """
     # Check if required columns exist in the dataframe
    required_columns = ['dT_obs', 'NDVI_model', 'Name', 'Veg']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe")
    
    # Extracting the station name and vegetation type
    station_name = df['Name'].iloc[0]
    vegetation = df['Veg'].iloc[0]
    
    # Calculating the correlation coefficient
    correlation = np.corrcoef(df['NDVI_model'], df['dT_obs'])[0, 1]
    
    # Creating the scatter plot with regression line
    plt.figure(figsize=(10, 6))
    sns.regplot(x='NDVI_model', y='dT_obs', data=df, scatter_kws={'s': 100, 'alpha': 1}, line_kws={'color': 'red'})
    # sns.regplot(x='NDVI_model', y='dT', data=df, scatter_kws={'s': 100, 'alpha': 1,'color': "k"}, line_kws={'color': 'red'})

    plt.title(f"Station: {station_name}, Vegetation: {vegetation}", fontsize=20)
    plt.xlabel("NDVI ", fontsize=20)
    plt.ylabel("Measured dT (C)", fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid(True)
    plt.ylim(-2,18)
    # Adding the correlation coefficient text
    plt.text(0.95, 0.85, f'r= {correlation:.2f}', 
             fontsize=25, 
             transform=plt.gca().transAxes,
             verticalalignment='bottom', 
             horizontalalignment='right')
    
    plt.show()


# Example usage:
# Assuming 'data' is your dataframe

#%%
## Timeseries 
import matplotlib.dates as mdates

def plot_time_series(df):
    """
    Plots a time series with 'Date' on the x-axis and 'dT_obs' and 'dT' on the y-axis.
    Points are marked by scatter and lines join the points. The title includes station name and vegetation.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the columns 'Date', 'dT_obs', 'dT', 'Name', and 'Veg'.
    """
    
    # Check if required columns exist in the dataframe
    required_columns = ["date", 'dT_obs', 'dT', 'Name', 'Veg']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe")
    
    # Ensure "date" column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    
    # Extracting the station name and vegetation type
    station_name = df['Name'].iloc[0]
    vegetation = df['Veg'].iloc[0]
    
    # Calculate percentage bias
    mean_bias = ((df['dT'] - df['dT_obs']).mean() / df['dT_obs'].mean()) * 100
    # mean_bias = bias.mean()
    
    # Creating the time series plot
    plt.figure(figsize=(14, 8))
    
    # Plotting 'dT_obs'
    plt.plot(df["date"], df['dT_obs'], marker='o', linestyle='-', label='Measured dT')
    plt.scatter(df["date"], df['dT_obs'], s=100, alpha=0.7)
    
    # Plotting 'dT'
    plt.plot(df["date"], df['dT'], marker='o', linestyle='-', label='dT SEBAL')
    plt.scatter(df["date"], df['dT'], s=100, alpha=0.7)
    
    # Formatting the plot
    plt.title(f"Station: {station_name}, Vegetation: {vegetation}", fontsize=20)
    # plt.xlabel("date", fontsize=20)
    plt.ylabel('dT (C)', fontsize=20)
    
    # Set x-axis major locator to AutoDateLocator and format the date
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)
    
    # Adding the percentage bias text
    plt.text(0.05, 0.95, f'Mean % Bias: {mean_bias:.2f}%', 
             fontsize=15, 
             transform=plt.gca().transAxes,
             verticalalignment='top', 
             horizontalalignment='left')
    
    # Formatting the ticks
    plt.xticks(fontsize=20, rotation=45)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=25,loc="upper right")
    plt.grid(True)
    plt.ylim(-1,20)

    plt.show()

for i in range(len(select_stations)):
    plot_dT_LST_scatter(select_stations[i])
    plot_time_series(select_stations[i])# select_stations[0].columns.tolist()

# %%
from sklearn.metrics import r2_score
from matplotlib.ticker import MaxNLocator

def calculate_metrics(df):
    """Calculate percentage bias and percentage RMSE."""
    # Calculate percentage bias
    mean_bias = ((df['dT'] - df['dT_obs']).mean() / df['dT_obs'].mean()) * 100
    # mean_bias = bias.mean()
    
    # Calculate percentage RMSE
    rmse = np.sqrt(((df['dT'] - df['dT_obs']) ** 2).mean())
    mean_obs = df['dT_obs'].mean()
    percent_rmse = (rmse / mean_obs) * 100
    return mean_bias, percent_rmse

def plot_dT_vs_dT_obs_scatter(df):
    """
    Plots a scatter plot between 'dT' and 'dT_obs' with the title including station name and vegetation.
    Also plots a 1:1 line and displays the coefficient of determination (R²) on the plot.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the columns 'dT', 'dT_obs', 'Name', and 'Veg'.
    """
    
    # Check if required columns exist in the dataframe
    required_columns = ['dT', 'dT_obs', 'Name', 'Veg']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe")
    
    # Extracting the station name and vegetation type
    station_name = df['Name'].iloc[0]
    vegetation = df['Veg'].iloc[0]
    
    # Calculating the coefficient of determination (R²)
    # r2 = r2_score(df['dT_obs'], df['dT'])
    # Calculating percentage bias and percentage RMSE
    mean_bias, percent_rmse = calculate_metrics(df)

    # Creating the scatter plot
    plt.figure(figsize=(8, 8))  # Set the figure size to be square
    sns.scatterplot(x='dT_obs', y='dT', data=df, s=100, color="tab:blue")
    
    # Plotting the 1:1 line
    min_val = -1
    max_val = 20
    plt.plot([min_val, max_val], [min_val, max_val], 'k--',linewidth=2)
    
    plt.title(f"Station: {station_name}, Vegetation: {vegetation}", fontsize=20)
    plt.xlabel("Measured dT (C)", fontsize=20)
    plt.ylabel("Estimated dT model (C)", fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid(True)
    
  # Adding the coefficient of determination, percentage bias, and percentage RMSE text
    plt.text(0.95, 0.05, f'% Bias: {mean_bias:.2f}%\n% RMSE: {percent_rmse:.2f}%', 
             fontsize=15, 
             transform=plt.gca().transAxes,
             verticalalignment='bottom', 
             horizontalalignment='right')
    plt.xlim(-1,20)
    plt.ylim(-1,20)
    # Ensure that x-ticks and y-ticks are integers
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tick_params(axis='both', which='major', labelsize=15)

    plt.show()
for i in range(len(select_stations)):
    plot_dT_vs_dT_obs_scatter(select_stations[i])
    plot_dT_NDVI_scatter(select_stations[i])
## Make US 