# -*- coding: utf-8 -*-
"""
Created on Mon May 27 15:36:47 2024

@author: chen
"""
import datetime as dt
from datetime import datetime

import mikeio
from mikecore.eum import eumUnit
from mikeio.eum import EUMType, ItemInfo
import numpy as np
from mikeio import Dfs2
import netCDF4 as nc
import xarray as xr
import os

folder_path="H:\era5"
ff=os.listdir(folder_path)
data=[]
for i in ff:
    u=xr.open_dataset(folder_path+"\\"+i)
    data.append(u)
data=xr.concat(data,dim='time')

#era=xr.open_dataset(r"H:\data\ocean2\era5.ocean_waves2.20170101.nc")
#data.variables
u10=np.array(data.variables['u10'][:])
v10=np.array(data.variables['v10'][:])
sp=np.array(data.variables['sp'][:])
time=np.array(data.variables['time'][:])

time_df=[]
tstart=datetime(2022,7,1,0)
for i in range(len(time)):
    time_df.append(tstart+dt.timedelta(hours=int(i)))

lon=np.array(data.variables['longitude'][:])
lat=np.flipud(np.array(data.variables['latitude'][:]))

dfsfile='F:\mikkk\HS\config\wind_era5.dfs2'
x0,y0=lon[0],lat[0]
dx,dy=0.25,0.25
time0=time_df[0]
delta_t=3600

items=[ItemInfo("u10",EUMType.Wind_speed,eumUnit.eumUmeterPerSec),
       ItemInfo("v10",EUMType.Wind_speed,eumUnit.eumUmeterPerSec),
       ItemInfo("ps",EUMType.Pressure, eumUnit.eumUPascal)]

geometry=mikeio.Grid2D(x0=117.0,nx=37,dx=dx,y0=28.0,ny=27,dy=dy,origin=(117,28),projection="LONG/LAT")

dfs=Dfs2()
d=[u10,v10,sp]#注意数据翻转问题
aa=mikeio.Dataset(data=d,time=time_df, items=items, geometry=geometry)

dfs.write(data=aa,filename=dfsfile, dt=delta_t,  title='wind_stuff')



ds=mikeio.read("F:\mikkk\HS\config\wind_era5.dfs2")

check=ds.to_xarray()
data=np.loadtxt("F:\mikkk\HS\config\wind_era5.txt")



#多月数据求平均写入dfs2

nc_files=sorted(glob.glob(r'G:\era5\wave\2013-winter\*.nc'))
out_dir=r'G:\250428dumping_sub\config\3#\waves_b\winter_wave.dfs2'

def nc_concat(nc_files):
    lon_range=(117,126.5)
    lat_range=(35,28)
    ds=xr.open_mfdataset(nc_files,combine="by_coords").sel(longitude=slice(*lon_range), latitude=slice(*lat_range))
    target_var=["shww","mdww","mpww"]
    ex_ds=ds[target_var]  
    ex_ds=ex_ds.interp(latitude=np.linspace(35, 28, 28),longitude=np.linspace(117, 126.5,38))
    ex_ds=ex_ds.sel(longitude=slice(117,126.25),latitude=slice(34.75,28))
    
    time=pd.to_datetime(ex_ds.time.values)
    ex_ds['year_month']=('time', [f"{t.year}-{t.month:02d}" for t in time])
    ex_ds['decade']=('time', (time.day-1)//10)
    grouped=ex_ds.groupby("year_month").apply(lambda x: x.groupby("decade").mean(dim="time"))
    
    all_data=[]
    time_s=[]
    for ym in grouped.year_month.values:
        decade_data=grouped.sel(year_month=ym)
        
        for decade in [0,1,2]:
            data=decade_data.sel(decade=decade)
            year, month=map(int, ym.split('-'))
            first_day=1 if decade==0 else 11 if decade==1 else 21 
            time_stamp=pd.Timestamp(year=year,
                                    month=month,
                                    day=first_day)
            
            shww=np.flip(data["shww"].values,axis=0)
            mdww=np.flip(data["mdww"].values,axis=0)
            mpww=np.flip(data["mpww"].values,axis=0)
            
            all_data.append((shww,mdww,mpww))
            time_s.append(time_stamp)
    return all_data,time_s

def write_dfs2(data, time, output_path):
    dx,dy=0.25,0.25
    
    grid=mikeio.Grid2D(x0=117.0,nx=37,dx=dx,y0=28.0,ny=27,dy=dy,origin=(117,28),projection="LONG/LAT")
    
    shww_a=np.array([d[0] for d in data])
    mdww_a=np.array([d[1] for d in data])
    mpww_a=np.array([d[2] for d in data])
    
    items=[ItemInfo("height",EUMType.Wave_height,eumUnit.eumUmeter),
           ItemInfo("direction",EUMType.Wave_direction,eumUnit.eumUdegree),
           ItemInfo("period",EUMType.Wave_period, eumUnit.eumUsec)]
    dfs=Dfs2()
    d=[shww_a,mdww_a,mpww_a]
    one_dfs=mikeio.Dataset(data=d,time=time,items=items,geometry=grid)
    dfs.write(data=one_dfs, filename=output_path, title='summer_wave')
    
all_data,time_s=nc_concat(nc_files)
write_dfs2(all_data, time_s, out_dir)    


