import pandas as pd 
import numpy as np 


import pandas as pd
import numpy as np

def sen1_ls_join(listofdf, time_lag):
    """
    Merging Sentinel-1 with Landsat.
    Time_lag: Forward fill up to how many points.
    """
    sen1_landsat = []
    columns_to_fill = ['date', 'VV', 'VH', 'angle']
    
    for df in listofdf:
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values('Date', inplace=True)
        
        # Add a column to track the gap in days
        df['Gap'] = pd.NA
        
        # Forward fill each column conditionally
        for column in columns_to_fill:
            last_value = None
            last_date = None
            fill_count = 0  # Counter to keep track of how many times we've filled
            
            for idx, row in df.iterrows():
                if pd.notna(row[column]):
                    last_value = row[column]
                    last_date = row['Date']
                    fill_count = 0  # Reset the counter when we encounter a new value
                elif last_value is not None and fill_count < time_lag:
                    df.at[idx, column] = last_value
                    df.at[idx, 'Gap'] = (row['Date'] - last_date).days
                    fill_count += 1
                elif fill_count >= time_lag:
                    last_value = None  # Reset last_value after filling the next two dates
        
        df.reset_index(drop=True, inplace=True)
        filtered_df = df[(df["NDVI"].notna()) & (df["VV"].notna())]
        
        if not filtered_df.empty:
            filtered_df = filtered_df.replace("<NA>", np.nan)
            filtered_df["Gap"] = filtered_df["Gap"].astype('Int64')
        
        sen1_landsat.append(filtered_df)
    
    return sen1_landsat

