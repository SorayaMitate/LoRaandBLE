#データに関するあれこれを行う処理

import csv
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from const import *
from func import *

const = Const()

#各種ファイル読み込み
path = '/home/owner/mitate/MieSCOPE/data/usingHMM/'
df = pd.read_csv(path + 'data/traj_2000.csv', index_col=0)
trans_prob_mat = np.loadtxt(path + 'data/TransProb_matrix.txt')
index_clusterNo_df = pd.read_csv(path + 'data/IndextoClusterNo_df.csv', index_col=0, \
    usecols=['indexName','ClusterNo'])
with open(path + 'data/Trajectory_list') as f:
    reader = csv.reader(f)
    traj_list = [row for row in reader]
print('len trajectory list =', len(traj_list))
observation = pd.read_csv(path + 'data/observationModel.csv',index_col=0)

#クラスタヘッドの配置図作成
#fig = plt.figure()
#ax = plt.axes()
#for i, row in df[df['clu_head']==True].iterrows():
#    ax.add_patch(patches.Circle(xy=(row['lat'], row['lon']), radius=50))
#plt.xlim(const.A, const.B)
#plt.ylim(const.A, const.B)
#plt.grid()
#plt.axis('scaled')
#ax.set_aspect('equal')

#plt.savefig('cluster_posi.png')

#クラスタ番号⇒インデックス
#出力：インデックス
def convertIndex(CluNum):
    return list(index_clusterNo_df[index_clusterNo_df['ClusterNo']==int(CluNum)].index)[0]

#クラスタ番号⇒インデクス
def convertClusterNO(index):
    return index_clusterNo_df.at[index,'ClusterNo']

#クラスタNo.のランダム選択()
#出力：インデックス
def randomCluNum():
    return random.choice(index_clusterNo_df.index.values)

#Trajectoryのランダム選択
#出力：Trajectoryリスト[クラスタNo....]
def randomTraj():
    return random.choice(traj_list)

#クラスタ番号⇒クラスタのxy座標
def CluNumtoPosi(cluNum):
    cluNum = index_clusterNo_df.loc[cluNum]['ClusterNo'] 
    x = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lat']
    y = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lon']
    return int(x), int(y)

def return_perAvg(cluNum):
    for i, v in observation[observation['cluNum']==int(cluNum)].iterrows():
        tmp = v['per_avg']
        break
    return tmp

#BLE通信の遅延計算
#入力：Cluster No., BLE APリスト
#出力：遅延時間(期待値)
def calc_delay_ble(cluNum, ble_ap_list):
    size = trans_prob_mat[cluNum].shape[0]
    l = [i for i in range(size) if trans_prob_mat[cluNum][i] > 0.0]

    tmp = [trans_prob_mat[cluNum][i] for i in range(size) if trans_prob_mat[cluNum][i] > 0.0]
    print('sum =',sum(tmp))

    ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]
    x1, y1 = CluNumtoPosi(cluNum)
    delay = 0.0
    for i in l:
        x2, y2 = CluNumtoPosi(i)
        dist_tmp = calc_dist(x1,y1,x2,y2)
        print('dist_tmp =',dist_tmp)
        if (i in ble_cluNum_list) == True:
            delay += trans_prob_mat[cluNum][i] * dist_tmp
        else:
            delay += trans_prob_mat[cluNum][i] * dist_tmp + const.PACKET/const.RATE[const.SF12]
    return delay / len(l)

#BLE通信の消費電流の計算
#入力：Cluster No., BLE APリスト, BLEの電流
#出力：消費電流(期待値)
def calc_energy_ble(cluNum, ble_ap_list, e_sf12):
    size = trans_prob_mat[cluNum].shape[0]
    l = [i for i in range(size) if trans_prob_mat[cluNum][i] > 0.0]
    ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]
    x1, y1 = CluNumtoPosi(cluNum)
    delay = 0.0
    for i in l:
        x2, y2 = CluNumtoPosi(i)
        dist_tmp = calc_dist(x1,y1,x2,y2)
        if (i in ble_cluNum_list) == True:
            delay += trans_prob_mat[cluNum][i] * (dist_tmp)*const.BLE_CURRENT['IDLE']
        else:
            delay += trans_prob_mat[cluNum][i] * dist_tmp*const.BLE_CURRENT['IDLE'] + e_sf12
    return delay / len(l)

#各メッシュの遷移先からPERを算出する処理
#入力 : ノードのcluNNum, 対象エリア(DF), SNR-PER曲線(システムごとのparam)
def calc_per(cluNum, area, snrper,pl):
    size = trans_prob_mat[cluNum].shape[0]
    trans_clu = [(index_clusterNo_df.at[i,'ClusterNo'], trans_prob_mat[cluNum][i]) \
        for i in range(size) if trans_prob_mat[cluNum][i] > 0.0]
    
    #per_aveの作成
    per = {system:0.0 for system in const.SF_LIST}
    per_ave = {system:0.0 for system in const.SF_LIST}

    #遷移先クラスタでループ
    for value in trans_clu:
        #遷移先毎のperを算出
        #areaとdfの対応
        posi = [(observation.at[i,'lat'],observation.at[i,'lon']) \
            for i in observation[observation['cluNum']==int(value[0])].index]
        #対応するarea(df)のインデックスをサーチ
        index = [area[(area['X']==int(v[0]))&(area['Y']==int(v[1]))].index[0] for v in posi\
            if (v[0]<const.B) and (v[1]<const.B)]
        
        if len(index) > 0:
            #各メッシュ毎のPERを算出
            for i in index:
                SNR = tvtodBm(dBmtotv(area.at[i,'SHADOWING']-pl+const.TPOW)\
                    /dBmtotv(const.AWGN))
                for system in const.SF_LIST:
                    if nonlinear_fit(SNR, *snrper[system]) >1.0:
                        tmp = 1.0
                    else:
                        tmp = nonlinear_fit(SNR, *snrper[system])
                    per[system] += value[1]*tmp

            for system in const.SF_LIST:            
                per_ave[system] += per[system] / len(index)

    for system in const.SF_LIST:
        per_ave[system] = per_ave[system] / len(trans_clu)

    per_ave[const.BLE] = 0.0001
    return per_ave

#クラスタごとの平均シャドウィング値を算出するプログラム
#入力 : area('lat','lon','shadowing','pathloss','cluNum','shadowing_avg'), 
#用いるdata：observation('lat','lon','cluNum','counts',trans_prob),
def calc_shadowingavg(area):
    for v in observation['cluNum'].value_counts().index:
        if v == -1:
            pass
        else:   
            tmp = 0.0
            index_list = []
            for i, row in observation[observation['cluNum']==v].iterrows():
                if (row['lat'] < const.B) and (row['lon'] < const.B):
                    j = area[(area['X']==int(row['lat']))&\
                        (area['Y']==int(row['lon']))].index[0]
                    tmp += area.at[j,'SHADOWING']
                    area.at[j,'cluNum'] = int(v)
                    index_list.append(j)
                
            #クラスタ毎の平均shadowing値を算出
            if len(observation[observation['cluNum']==v]) > 0:
                tmp = tmp / len(observation[observation['cluNum']==v])
                for i in index_list:
                    area.at[i,'shadowing_avg']=tmp
            else:
                pass

    return area
