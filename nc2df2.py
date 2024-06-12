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
