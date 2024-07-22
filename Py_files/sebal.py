import ee
from datetime import date
import folium
import geemap
import ipyleaflet
import matplotlib.pyplot as plt
from geemap import cartoee
import numpy as np
import cartopy as ccrs
import geemap.colormaps as cm
import pandas as pd
import datetime
from datetime import datetime, timedelta
from collections import OrderedDict
from calendar import monthrange
ee.Initialize()
import sys
sys.path.append('D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\geeSEBAL_copy_edits\\etbrasil\\')
import geesebal
from geesebal import (tools,landsatcollection,masks,meteorology,endmembers, 
evapotranspiration,collection,timeseries,image,ET_Collection_mod)

#----- Function to run Sebal
def et_collection_SR(start_date,end_date,lon,lat,scale):
    geometry=ee.Geometry.Point([lon,lat])
    ls=ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").filterDate(start_date,end_date).filterMetadata('CLOUD_COVER', 'less_than',75 )
    ls=ls.filterBounds(geometry)
    def applyScaleFactors(image):
        opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
        thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
        return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)
    ls=ls.map(applyScaleFactors)
#    ls = ls.filter(ee.Filter.neq('system:index','LC08_038037_20210903'));
    ls_list=ls.aggregate_array('system:index').getInfo()
    # print(ls_list)
    count = ls.size().getInfo()
    print("Number of scenes: ", count)
    n=0
    k=0
    lon_cold_pixel=[]
    lat_cold_pixel=[]
    ts_cold_scene=[]
    cold_pixel_lat,cold_pixel_lon,cold_pixel_ndvi,cold_pixel_temp,cold_pixel_sum=[],[],[],[],[]
    hot_pixel_lat,hot_pixel_lon,hot_pixel_ndvi,hot_pixel_temp,hot_pixel_sum=[],[],[],[],[]
    hot_pixel_Rn,hot_pixel_G=[],[]
    zenith_angle=[]
    #====== ITERATIVE PROCESS ======#
    #FOR EACH IMAGE ON THE LIST
    #ESTIMATE ET DAILY IMAGE
    while n < count:
        #GET IMAGE
        image= ls.filterMetadata('system:index','equals',ls_list[n]).first()
        image.getInfo()
        image=ee.Image(image)
        NDVI_cold=5
        Ts_cold=20
        NDVI_hot=10
        Ts_hot=20
        index=image.get('system:index')
        cloud_cover=image.get('CLOUD_COVER')
        LANDSAT_ID=image.get('L1_LANDSAT_PRODUCT_ID').getInfo()
        print(LANDSAT_ID)
        landsat_version=image.get('SATELLITE').getInfo()
        sun_elevation=image.get("SUN_ELEVATION")
        print(sun_elevation.getInfo())
        time_start=image.get('system:time_start')
        date=ee.Date(time_start)
        year=ee.Number(date.get('year'))
        month=ee.Number(date.get('month'))
        day=ee.Number(date.get('day'))
        hour=ee.Number(date.get('hour'))
        minuts = ee.Number(date.get('minutes'))
        print(str(hour.getInfo())+str(minuts.getInfo()))
        crs = image.projection().crs()
        transform=ee.List(ee.Dictionary(ee.Algorithms.Describe(image.projection())).get('transform'))
        date_string=date.format('YYYY-MM-dd').getInfo()
        #ENDMEMBERS
        p_top_NDVI=ee.Number(NDVI_cold)
        p_coldest_Ts=ee.Number(Ts_cold)
        p_lowest_NDVI=ee.Number(NDVI_hot)
        p_hottest_Ts=ee.Number(Ts_hot)
        ls_trial=image.select([0,1,2,3,4,5,6,8,17], ["UB","B","GR","R","NIR","SWIR_1","SWIR_2","ST_B10","pixel_qa"])
#       ls.first_toa=ee.Image('LANDSAT/LC08/C01/T1/'+index.getInfo())
        ls_trial=masks.f_cloudMaskL8_SR(ls_trial)
#         print("Cloud masking Complete")
        #ALBEDO TASUMI ET AL. (2008) METHOD WITH KE ET AL. (2016) COEFFICIENTS
        ls_trial=masks.f_albedoL8(ls_trial)
        #------ Meteorology
          #GEOMETRY
        geometryReducer=ls_trial.geometry().bounds().getInfo()
        geometry_download=geometryReducer['coordinates']
        #METEOROLOGY PARAMETERS
        col_meteorology= meteorology.get_meteorology(ls_trial,time_start);
        #AIR TEMPERATURE [C]
        T_air = col_meteorology.select('AirT_G');
        #WIND SPEED [M S-1]
        ux= col_meteorology.select('ux_G');
        #RELATIVE HUMIDITY [%]
        UR = col_meteorology.select('RH_G');
        #NET RADIATION 24H [W M-2]
        Rn24hobs = col_meteorology.select('Rn24h_G');
        print("Metorology ready")
        #------
        #------ Elevation
        #SRTM DATA ELEVATION
        SRTM_ELEVATION ='USGS/SRTMGL1_003'
        srtm = ee.Image(SRTM_ELEVATION).clip(geometryReducer);
        z_alt = srtm.select('elevation')
## print(z_alt) 
        ls_trial=tools.fexp_spec_ind(ls_trial)
        ls_trial=tools.LST_DEM_correction(ls_trial, z_alt, T_air, UR,sun_elevation,hour,minuts)
## GET IMAGE
## COLD PIXEL
        d_cold_pixel=endmembers.fexp_cold_pixel(ls_trial, geometryReducer, p_top_NDVI, p_coldest_Ts)
        print(d_cold_pixel.getInfo())
## COLD PIXEL NUMBER
        n_Ts_cold = ee.Number(d_cold_pixel.get('temp').getInfo())
##INSTANTANEOUS OUTGOING LONG-WAVE RADIATION [WM-2]
        ls_trial=tools.fexp_radlong_up(ls_trial)
##INSTANTANEOUS INCOMING SHORT-WAVE RADIATION [WM-2]
        ls_trial=tools.fexp_radshort_down(ls_trial,z_alt,T_air,UR, sun_elevation)
## INSTANTANEOUS INCOMING LONGWAVE RADIATION [W M-2]
        ls_trial=tools.fexp_radlong_down(ls_trial, n_Ts_cold)
##INSTANTANEOUS NET RADIATON BALANCE [W M-2]
        ls_trial=tools.fexp_radbalance(ls_trial)
##SOIL HEAT FLUX (G) [W M-2]
        ls_trial=tools.fexp_soil_heat(ls_trial)
##HOT PIXEL
        d_hot_pixel=endmembers.fexp_hot_pixel(ls_trial, geometryReducer,p_lowest_NDVI, p_hottest_Ts)
##SENSIBLE HEAT FLUX (H) [W M-2]
        ls_trial=tools.fexp_sensible_heat_flux(ls_trial, ux, UR,Rn24hobs,n_Ts_cold,
                                       d_hot_pixel, date_string,geometryReducer)
##DAILY EVAPOTRANSPIRATION (ET_24H) [MM DAY-1]
        ls_trial=evapotranspiration.fexp_et(ls_trial,Rn24hobs)
## Store all the values of the cold pixel 
        cold_pixel_lat.append(d_cold_pixel.get("y").getInfo())
        cold_pixel_lon.append(d_cold_pixel.get("x").getInfo())
        cold_pixel_temp.append(d_cold_pixel.get("temp").getInfo())
        cold_pixel_ndvi.append(d_cold_pixel.get("ndvi").getInfo())
        cold_pixel_sum.append(d_cold_pixel.get("sum").getInfo())
## Get info about hot pixl
        hot_pixel_lat.append(d_hot_pixel.get("y").getInfo())
        hot_pixel_lon.append(d_hot_pixel.get("x").getInfo())
        hot_pixel_temp.append(d_hot_pixel.get("temp").getInfo())
        hot_pixel_ndvi.append(d_hot_pixel.get("ndvi").getInfo())
        hot_pixel_sum.append(d_hot_pixel.get("sum").getInfo())
        hot_pixel_Rn.append(d_hot_pixel.get("Rn").getInfo())
        hot_pixel_G.append(d_hot_pixel.get("G").getInfo())
        zenith_angle.append(90-sun_elevation.getInfo())

        NAME_FINAL=LANDSAT_ID[:5]+LANDSAT_ID[10:17]+LANDSAT_ID[17:25]
        if k ==0:
            new_ls=ee.List([])
            met=ee.List([])
            new_ls=new_ls.add(ls_trial)
            met=met.add(col_meteorology.select("Rn24h_G","AirT_G","RH_G","ux_G","SW_Down"))
        else:
            new_ls=new_ls.add(ls_trial)
            met=met.add(col_meteorology.select("Rn24h_G","AirT_G","RH_G","ux_G","SW_Down"))
        k=k+1
        n=n+1
        ## Convert to dataframe 
        et_collection=ee.ImageCollection(new_ls)
        met_collection=ee.ImageCollection(met)
        ##Get the values
        region = et_collection.getRegion(geometry, int(scale),crs="EPSG:4326").getInfo()
        era5_met=met_collection.getRegion(geometry, int(scale),crs="EPSG:4326").getInfo()
# stuff the values in a dataframe for convenience      
    df = pd.DataFrame.from_records(region[1:len(region)])
    df_met = pd.DataFrame.from_records(era5_met[1:len(era5_met)])
    if df.shape == (0,0):
        return pd.DataFrame()
    else:
        # use the first list item as column names
        df.columns = region[0]
        df_met.columns=era5_met[0]
        df_met=df_met.drop(["time"],axis=1)
        print(df_met)
        df=pd.concat([df,df_met],axis=1)
#    cold_pixel_lat,cold_pixel_lon,cold_pixel_ndvi,cold_pixel_temp,cold_pixel_sum
        df["cold_pixel_lat"]=cold_pixel_lat
        df["cold_pixel_lon"]=cold_pixel_lon
        df["cold_pixel_ndvi"]=cold_pixel_ndvi
        df["cold_pixel_sum"]=cold_pixel_sum
        df["cold_pixel_temp"]=cold_pixel_temp
## Hot pixel
        df["hot_pixel_sum"]=hot_pixel_sum
        df["hot_pixel_lat"]=hot_pixel_lat
        df["hot_pixel_lon"]=hot_pixel_lon
        df["hot_pixel_ndvi"]=hot_pixel_ndvi
        df["hot_pixel_Rn"]=hot_pixel_Rn
        df["hot_pixel_G"]=hot_pixel_G
        df["hot_pixel_temp"]=hot_pixel_temp
        df.time = df.time / 1000
        df['time'] = pd.to_datetime(df['time'], unit = 's')
        df.rename(columns = {'time': 'date'}, inplace = True)
        df.sort_values(by = 'date')
        return df
    
## Define a function to split the duration to bypass earth engine timeo outs for large collections
## Define a function to split the calls 
def split_years(start_date, end_date):
    """
    Function to split query period to bypass computation timed out (300s query limit of gee)
    Takes input as start and end years
    Gives output as list of start and end periods for each year
    """
  
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in [start_date, end_date]]
    start = list(OrderedDict(((start + timedelta(_)).strftime(r"%Y-%m-01"), None) for _ in range((end - start).days)).keys())
    end = [item[:-2]+str(monthrange(int(item[:4]),int(item[5:7]))[1]) for item in start] 
    return start,end

## Final function call to make the sebal call 
def call_et_func(lon,lat,start_date,end_date,scale,name,dir):
        """
        This the function to be called from any script
        It will give daily ET at pixel value at desired scale 
        The output files will be in .csv format 
        Start date, End date: Strings
        Naming: They will be saved in "name" folder and all overpass in each month will 
        be saved as mm-dd-yy for each month contaiing daily ET 
        """
        start,end=split_years(start_date,end_date)
        # print(start,end)
        concat=pd.DataFrame()
        for i in range(len(start)):
                try:
                    df_sub=et_collection_SR(start[i],end[i],lon,lat,scale)
                    print(start[i])
                    df_sub.to_csv(dir+name+"\\"+str(start[i])+".csv")
                    # concat = pd.concat([concat, df_sub], axis = 0) 
                except:
                    pass
        return concat