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

#path = 'C:\\Users\\soraya-PC\\code\\results\\system\\5\\'
path = 'C:\\Users\\soraya-PC\\code\\results\\system\\5\\shaped\\'
file_list = glob.glob(path+'*')

sns.set_style("darkgrid")

#fig = plt.figure()
#ax = Axes3D(fig)

#ax.set_xlabel("distance between transmitter and receiver")
#ax.set_ylabel("shadowing")
#ax.set_zlabel("system")

const = Const()

'''
BIN = 200
dist_bin = np.arange(BIN, 1400, BIN)

fig, ax = plt.subplots(figsize=(10, 8))
for_replace = r'C:\\Users\\soraya-PC\\code\\results\\system\\5\\'
for f in file_list:
    df = pd.read_csv(f)
    
    #結果格納用
    result = {'dist':[],const.SF7:[],const.SF8:[],const.SF10:[]\
        ,const.SF11:[],const.SF12:[],const.BLE:[]} 

    for d in dist_bin:
        result['dist'].append(d)
        tmp = df[(d-BIN<=df['dist'])&(df['dist']<d)]
        
        for system in const.SYSTEM_LIST:
            result[system].append(len(tmp[tmp['clu_system']==system]) / len(tmp))
    
    #ファイル名の置換
    file_name = f.replace(path,'re')
    tmp = pd.DataFrame(result.values(), index=result.keys()).T
    tmp.to_csv(path+file_name)
'''

'''
fig, ax = plt.subplots(2, 2)
plt.style.use('ggplot') 
font = {'family' : 'meiryo'}
matplotlib.rc('font', **font)

df = {}
file_name = {}
for i in range(len(file_list)):
    df[i] = pd.read_csv(file_list[i],index_col='dist', dtype={'dist':int})
    df[i] = df[i].drop('Unnamed: 0', axis=1)
    df[i] = df[i].rename(columns={str(const.SF7):'SF7',str(const.SF8):'SF8',\
        str(const.SF10):'SF10',str(const.SF11):'SF11',str(const.SF12):'SF12',\
            str(const.BLE):'BLE'})
    file_name[i] = file_list[i].replace(path+'re','')
    file_name[i] = file_name[i].replace('system_results.csv','')

for i in range(len(df)):
    if i < 2:
        df[i].plot.bar(ax=ax[0,i],title=file_name[i],fontsize=20,grid=True,legend=True,stacked=True,)
        ax[0,i].set_xlabel('')
        ax[0,i].legend(loc='upper right',fontsize=15)
    else:
        tmp = i-2
        df[i].plot.bar(ax=ax[1,tmp],title=file_name[i],fontsize=20,grid=True,legend=True,stacked=True,)
        ax[1,tmp].set_xlabel('')
        ax[1,tmp].legend(loc='upper right',fontsize=15)

plt.subplots_adjust(hspace=0.3)
plt.show()
#plt.savefig(file_name)
'''

'''
path = 'C:\\Users\\soraya-PC\\code\\results\\app\\5\\'
file_name = 'results.csv'
df = pd.read_csv(path+file_name,index_col='app')
df = df.drop('Unnamed: 0', axis=1)

plt.style.use('ggplot') 
font = {'family' : 'meiryo'}
matplotlib.rc('font', **font)
df.plot.bar(fontsize=20,grid=True,legend=True)
plt.show()
'''

import csv 
from func import *

def hist_cluster():

    path = '/home/owner/mitate/MieSCOPE/data/usingHMM/'
    df = pd.read_csv(path + 'data/traj_2000.csv', index_col=0)
    with open(path + 'data/Trajectory_list') as f:
        reader = csv.reader(f)
        traj_list = [row for row in reader]

    dist = []
    print(df)
    for traj in traj_list:
        flag = 0
        for clu in traj:
            if flag == 0:
                x_tmp = df[(df['cluNum']==int(clu))&(df['clu_head']==True)]['lat']
                y_tmp = df[(df['cluNum']==int(clu))&(df['clu_head']==True)]['lon']
                flag = 1
            else:
                x = df[(df['cluNum']==int(clu))&(df['clu_head']==True)]['lat']
                y = df[(df['cluNum']==int(clu))&(df['clu_head']==True)]['lon']
                dist.append(calc_dist(x_tmp,y_tmp,x,y))
                x_tmp = x
                y_tmp = y
    path = '/home/owner/mitate/MieSCOPE/LoRaandBLE/results/'
    dist_df = pd.Series(dist,name='dist')
    dist_df.to_csv(path+'cluster_dist.csv')

hist_cluster()

