# -*- coding: utf-8 -*-
"""
Created on Fri May 31 15:36:14 2024

@author: chen
"""

import pandas as pd
import numpy as np


reference=pd.read_excel(r"F:\mikkk\HS\config\reference_22_uu.xlsx",sheet_name="Sheet2",header=None)


f=open(r'F:\mikkk\HS\config\wind_era5_py.txt')
txt=[]
for line in f.readlines():
    line=line.strip("\n")
    ll=line.split()
    if len(ll)==37:
        txt.append(ll)

data=[]
for i in range(0,len(txt)-27+1,27):
    one=txt[i:i+27]
    one=np.array(one)
    data.append(one)

ni,nj=reference.shape#i27,j37
#reference37,27；data27,37
#reference[35][11],data[0][11][35]
recod=[]
for i in range(len(reference)):
    line=[]
    for j in range(nj):
        if reference[j][i]==10:
            line.append(j)
    recod.append(line)

stu={}
for r in range(len(recod)):#
    #stu=[]
    indexxx=[]
    for o in range(1,len(recod[r])):
        if recod[r][o]-recod[r][o-1]>1:
            indexxx.append(o)   
    if len(indexxx)==0:
        stu[r]=recod[r][:]
    if len(indexxx)==1:
        stu[r]=[recod[r][:indexxx[0]],recod[r][indexxx[0]:]]     #indexxx是序号，要换成数值
    elif len(indexxx)>1:
        stu[r]=[recod[r][:indexxx[0]]]
        for i in range(1,len(indexxx)):
            stu[r].append(recod[r][indexxx[i-1]:indexxx[i]])
        stu[r].append(recod[r][indexxx[-1]:])
            
data=np.array(data)

for s in stu:
    if len(stu[s])<37:
        for iner in range(len(stu[s])):
            data[:,s,stu[s][iner][0]:stu[s][iner][-1]+1]=1E-035
    else:
        data[:,s,:]= 1E-035


txt_file="F:\mikkk\HS\config\wind_canb_use.txt"
with open(txt_file,'w',encoding="utf-8") as f:
    for x in range(0,len(data)-3+1,3):
        wri=data[x:x+3]
        for w in range(len(wri)):
            f.write("\"tstep\""+" "+str(int(x/3))+" \"item\""+" "+str(w+1)+" "+"\"layer\""+" 0"+"\n")
            for h in range(len(wri[w])):
                tt=''
                for l in range(len(wri[w][h])):
                    tt=tt+wri[w][h][l]+' '
                tt=tt+'\n'
                f.write(tt)
            f.write('\n')
                    
            
            for x in range(len(wri[w])):
                f.write(str(wri[w][x])+'\n')
            

#reference 是输出数据做的dfs2，根据此修改era5，  注意数据好像要上下翻转
