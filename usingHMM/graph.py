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
from func import calc_dist

#mesh = pd.read_csv('SC_shadowing.csv')
#mesh = mesh[(mesh['X']<=1000)&(mesh['Y']<=1000)]

#pivot = mesh.pivot_table(values=['SHADOWING'], index=['X'], columns=['Y'], dropna= False)
#plt.figure()
#sns.heatmap(pivot,cmap = 'jet', linecolor='Black',square = True)
#plt.show()

#path = 'C:\\Users\\soraya-PC\\code\\data\\result\\backup\\sr\\qos2\\'
path = 'C:\\Users\\soraya-PC\\code\\data\\result\\backup\\sr\\qos2_noshad\\'
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
#plt.show()

def cl_density():
    
    #データファイル読み込み
    #path = '/home/owner/mitate/MieSCOPE/data/usingHMM/'
    path = '/home/flab/mitate/data/MieSCOPE/usingHMM/' #flab@192.168.7.247
    data = pd.read_csv(path + 'trajectory.csv', index_col=0)

    dist_cl = []
    dist_ap = []
    ap_x = float(const.B / 2)
    ap_y = float(const.B / 2)

    traj = list(df['tra_num'].unique())
    for tra in traj:
        tmp = data[data['tra_num']==tra]
        if tmp.empty:
            pass
        else:
            #最初の行取り出し
            head = int(tmp.head(1).index[0])
            for k, v in tmp.iterrows():
                if k == head:
                    x1 = float(v['lat'])
                    y1 = float(v['lon'])
                    pass
                else:
                    x2 = float(v['lat'])
                    y2 = float(v['lon'])
                    dist_cl.append(calc_dist(x1,y1,x2,y2))
                    dist_ap.append(calc_dist(x1,y1,ap_x,ap_y))
                    x1 = x2
                    y1 = y2
    
    df = pd.DataFrame({
        'dist_clu':dist_cl,
        'dist_ap':dist_ap
    })
    df.to_csv('dist.csv')
cl_density()