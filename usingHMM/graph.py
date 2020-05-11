import re
import random
from math import pi, log10, cos, sqrt
from cmath import exp as cexp
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib
import matplotlib.pyplot as plt
import glob
import seaborn as sns   
from mpl_toolkits.mplot3d import Axes3D

from const import *

#mesh = pd.read_csv('SC_shadowing.csv')
#mesh = mesh[(mesh['X']<=1000)&(mesh['Y']<=1000)]

#pivot = mesh.pivot_table(values=['SHADOWING'], index=['X'], columns=['Y'], dropna= False)
#plt.figure()
#sns.heatmap(pivot,cmap = 'jet', linecolor='Black',square = True)
#plt.show()

path = 'C:\\Users\\soraya-PC\\code\\data\\result\\UsedSystem\\'
file_list = glob.glob(path+'*')

sns.set_style("darkgrid")

#fig = plt.figure()
#ax = Axes3D(fig)

#ax.set_xlabel("distance between transmitter and receiver")
#ax.set_ylabel("shadowing")
#ax.set_zlabel("system")

const = Const()

BIN = 200
DIST_BIN = np.arange(BIN, 1400, BIN)

fig, ax = plt.subplots(2, 2)
plt.style.use('ggplot') 
font = {'family' : 'meiryo'}
matplotlib.rc('font', **font)

for i in range(len(file_list)):
    print('file name=',file_list[i])

    df = pd.DataFrame(index=DIST_BIN, columns=const.SYSTEM_LIST)
    data = pd.read_csv(file_list[i],dtype={'system':int})    

    #df[i] = pd.read_csv(file_list[i],index_col='dist', dtype={'dist':int})
    #df[i] = df[i].drop('Unnamed: 0', axis=1)
    for b in DIST_BIN:
        tmp = data[(data['dist']>=(b-BIN))&(data['dist']<b)]
        leng = len(tmp)
        for system in const.SYSTEM_LIST:
            kaisu = (tmp['system'] == system).sum()
            df.at[b,system] = float(kaisu / leng)

    df = df.rename(columns={const.SF7:'SF7',const.SF8:'SF8',\
        const.SF10:'SF10',const.SF11:'SF11',const.SF12:'SF12',\
            const.BLE:'BLE'})
    
    #file_name[i] = file_list[i].replace(path+'re','')
    #file_name[i] = file_name[i].replace('system_results.csv','.png')

    if i < 2:
        df.plot.bar(ax=ax[0,i],title=file_list[i],fontsize=20,grid=True,legend=True,stacked=True,)
        ax[0,i].set_xlabel('')
        ax[0,i].legend(loc='upper right',fontsize=15)
    else:
        tmp = i-2
        df.plot.bar(ax=ax[1,tmp],title=file_list[i],fontsize=20,grid=True,legend=True,stacked=True,)
        ax[1,tmp].set_xlabel('')
        ax[1,tmp].legend(loc='upper right',fontsize=15)
plt.show()

'''
for i in range(len(df)):
    print(file_name[i])
    df[i].plot.bar(fontsize=30,grid=True,legend=True,stacked=True,)
    plt.xlabel('Distance between LoRa GW and Mobile Node [m]',fontsize=30)
    plt.ylabel('Percentage of selected systems',fontsize=30)
    plt.legend(loc='upper right',fontsize=30)
    plt.show()
    #plt.savefig(file_name[i])
'''
'''
path = 'C:\\Users\\soraya-PC\\code\\results\\app\\5\\'
path = 'C:\\Users\\soraya-PC\\Desktop\\ieice-eng\\results\\app\\'
file_name = 'results.csv'
#df = pd.read_csv(path+file_name,index_col='app')
df = pd.read_csv(path+file_name)
#df = df.drop('Unnamed: 0', axis=1)
for k,row in df.iterrows():
    df.at[k,'PER'] = 1.0-df.at[k,'PER'] 

qos = [row['app'] for i,row in df.iterrows()]
for i in range(len(qos)):
    qos[i] = 'App.' + str(i+1)
per = [row['PER'] for i,row in df.iterrows()]
ene = [row['energy'] for i,row in df.iterrows()]
delay = [row['delay'] for i,row in df.iterrows()]

#fig, ax = plt.subplots(1, 3)
plt.style.use('ggplot') 
font = {'family' : 'meiryo'}
matplotlib.rc('font', **font)

#plt.subplot(1,3,1)
plt.bar(qos,per,align="center")
plt.xlabel('QoS Parameter with The Highest Priority',fontsize=30)
plt.ylabel('Packet Error Rate [%]',fontsize=30)
plt.tick_params(labelsize=30)
plt.grid(True)
plt.show()

#plt.subplot(1,3,2)
plt.bar(qos,delay,color="#1E7F00",align="center")
plt.xlabel('QoS Parameter with The Highest Priority',fontsize=30)
plt.ylabel('Current consumption [mA]',fontsize=30)
plt.tick_params(labelsize=30)
plt.grid(True)
plt.show()

#plt.subplot(1,3,3)
plt.bar(qos,ene,color="#1E7F00",align="center")
plt.xlabel('QoS Parameter with The Highest Priority',fontsize=30)
plt.ylabel('Transmission Delay [s]',fontsize=30)
plt.tick_params(labelsize=30)
plt.grid(True)
plt.show()
'''

def hist():
    file_name = 'cluster_dist.csv'
    df = pd.read_csv(file_name)
    print(df.columns)
    df = df.sort_values('dist')

    leng = len(df)
    BIN = 10
    l = np.arange(100,210,BIN)
    result = []
    for b in l:
        tmp = df[(b<=df['dist'])&(df['dist']<b+BIN)]
        result.append(len(tmp)/leng)
    print(result)

    l = [i+5 for i in l]

    fig = plt.figure()
    plt.style.use('ggplot') 
    font = {'family' : 'meiryo'}
    matplotlib.rc('font', **font)
    plt.bar(l,result,width=10)
    #plt.xlabel("xlabel", fontsize=20)
    #plt.ylabel("ylabel", fontsize=20)
    #plt.legend(loc='upper right',fontsize=20)
    plt.tick_params(labelsize=40)
    plt.show()

