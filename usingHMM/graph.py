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

const = Const()

#クラスタAP間距離と選択されたシステムの関係
def graph_usedsystem():
    path = 'C:\\Users\\soraya-PC\\code\\data\\result\\UsedSystem\\'
    file_list = glob.glob(path+'*')

    sns.set_style("darkgrid")

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

#APクラスタ間距離とクラスタ間距離の導出
def cl_density():
    
    #データファイル読み込み
    #path = '/home/owner/mitate/MieSCOPE/data/usingHMM/'
    path = '/home/flab/mitate/data/MieSCOPE/usingHMM/' #flab@192.168.7.247
    data = pd.read_csv(path + 'trajectory.csv', index_col=0)
    data = data.drop(data[data['cluNum']==-1].index)
    data = data.reset_index()

    dist_cl = []
    dist_ap = []
    ap_x = float(const.B / 2)
    ap_y = float(const.B / 2)

    traj = list(data['tra_num'].unique())
    for tra in traj:
        tmp = data[data['tra_num']==tra]
        if tmp.empty:
            pass
        else:
            tmp_clu = -1
            for cluNum in tmp['cluNum']:
                if tmp_clu == -1:
                    tmp_clu = cluNum
                    x1 = float(data[(data['cluNum']==tmp_clu)&(data['clu_head']==True)]['lat'])
                    y1 = float(data[(data['cluNum']==tmp_clu)&(data['clu_head']==True)]['lon'])

                else:
                    if tmp_clu != cluNum:
                        tmp_clu = cluNum
                        x2 = float(data[(data['cluNum']==tmp_clu)&(data['clu_head']==True)]['lat'])
                        y2 = float(data[(data['cluNum']==tmp_clu)&(data['clu_head']==True)]['lon'])

                        dist_cl.append(calc_dist(x1,y1,x2,y2))
                        dist_ap.append(calc_dist(x1,y1,ap_x,ap_y))

                        x1 = x2
                        y1 = y2

                    else:
                        pass

    df = pd.DataFrame({
        'dist_clu':dist_cl,
        'dist_ap':dist_ap
    })
    df.to_csv('dist.csv')
#cl_density()

def hist():
    MAX_DIST = 1200
    DIST_BIN = 200

    MAX_DIST = 1000
    DIST_BIN = 500

    DIST = np.arange(0,MAX_DIST,DIST_BIN)

    MAC_CLU_DIST = 200
    MIN_CLU_DIST = 100
    CLU_DIST_BIN = 10
    CLU_DIST = np.arange(MIN_CLU_DIST,MAC_CLU_DIST,CLU_DIST_BIN)

    df = pd.DataFrame(index=CLU_DIST,columns=DIST)
    print('df =',df)

    data = pd.read_csv('dist.csv')

    for b in range(0, MAX_DIST, DIST_BIN):
        tmp = data[(data['dist_ap']>=b)&(data['dist_ap']<b+DIST_BIN)]
        avg = tmp['dist_clu'].mean()
        std = tmp['dist_clu'].std()

        print('bin =',b)
        print('average =',avg)
        print('std =',std)

        leng = len(tmp)
        for d in range(MIN_CLU_DIST,MAC_CLU_DIST,CLU_DIST_BIN):
            tmp2 = tmp[(tmp['dist_clu']>=d)&(tmp['dist_clu']<d+CLU_DIST_BIN)]
            df.at[d,b] = float(len(tmp2))/float(leng)

    df.to_csv('hist.csv')

def cl_graph():

    path = '/home/flab/mitate/data/MieSCOPE/usingHMM/' #flab@192.168.7.247
    data = pd.read_csv(path + 'trajectory.csv', index_col=0)

    tmp = data[data['clu_head']==True]
    x = list(tmp['lat'])
    y = list(tmp['lon'])

    plt.scatter(x,y, s=100)
    plt.savefig('Cluster.png')


def graph_hist():

    data = pd.read_csv('hist.csv',index_col=0)

    MAX_DIST = 1200
    #DIST_BIN = 200
    DIST_BIN = 600
    DIST = np.arange(0,MAX_DIST,DIST_BIN)
    leng = len(DIST)

    fig, ax = plt.subplots(1, 2)
    plt.subplots_adjust(wspace=0.3, hspace=0.5)
    plt.subplots_adjust(bottom=0.2)
    plt.style.use('ggplot') 
    font = {'family' : 'meiryo'}
    matplotlib.rc('font', **font)

    for i in range(leng):

        data.plot.bar(y=[str(DIST[i])],ax=ax[i],title=('D_ap='+str(DIST[i])+'[m]'),fontsize=20,grid=True,legend=False,ylim=[0.0,1.0])
        ax[i].set_xlabel('現クラスタと遷移先クラスタ間の距離 [m]',fontname="HGGothicM",fontsize=20)
        ax[i].set_ylabel('発生確率',fontname="HGGothicM",fontsize=20)

        '''
        if i < 3:
            data.plot.bar(y=[str(DIST[i])],ax=ax[0,i],title=('D_ap='+str(DIST[i])+'[m]'),fontsize=10,grid=True,legend=False,ylim=[0.0,1.0])
            ax[0,i].set_xlabel('Distance bettween Clusters [m]',fontsize=15)
            ax[0,i].set_ylabel('PDF',fontsize=15)
        else:
            tmp = i-3
            data.plot.bar(y=[str(DIST[i])],ax=ax[1,tmp],title=('D_ap='+str(DIST[i])+'[m]'),fontsize=10,grid=True,legend=False,ylim=[0.0,1.0])
            ax[1,tmp].set_xlabel('Distance bettween Clusters [m]',fontsize=15)
            ax[1,tmp].set_ylabel('PDF',fontsize=15)
        '''

    plt.show()


#cl_density()
#cl_graph()
hist()
#graph_hist()
#graph_usedsystem()