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
observation = pd.read_csv(path + 'data/observationModel.csv',index_col=0)

#クラスタヘッドの配置図作成
fig = plt.figure()
ax = plt.axes()
for i, row in df[df['clu_head']==True].iterrows():
    ax.add_patch(patches.Circle(xy=(row['lat'], row['lon']), radius=10))
plt.xlim(const.A, const.B)
plt.ylim(const.A, const.B)
plt.grid()
plt.axis('scaled')
ax.set_aspect('equal')

plt.savefig('cluster_posi.png')

#クラスタ番号⇒インデックス
#出力：インデックス
def convertIndex(CluNum):
    return list(index_clusterNo_df[index_clusterNo_df['ClusterNo']==int(CluNum)].index)[0]

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
    return float(x), float(y)

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
    ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]
    x1, y1 = CluNumtoPosi(cluNum)
    delay = 0.0
    for i in l:
        x2, y2 = CluNumtoPosi(i)
        dist_tmp = calc_dist(x1,y1,x2,y2)
        if (i in ble_cluNum_list) == True:
            delay += trans_prob_mat[cluNum][i] * dist_tmp
        else:
            delay += trans_prob_mat[cluNum][i] * dist_tmp + const.PACKET/const.RATE[const.SF12]
    return delay / len(l)

#各メッシュの遷移先からPERを算出する処理
#入力 : ノードのcluNNum, 対象エリア(DF), SNR-PER曲線
def calc_per(cluNum, area, snrper):
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
        index = [area[(area['X']==v[0])&(area['Y']==v[1])].index[0] for v in posi]
        #各メッシュ毎のPERを算出
        for i in index:
            for system in const.SF_LIST:
                per[system] += value[1]*snrper[system]((area.at[i,'SHADOWING']\
                    +area.at[i,'PL']))

        for system in const.SF_LIST:            
            per_ave[system] += per[system] / len(index)

    for system in const.SF_LIST:
        per_ave = per_ave[system] / len(trans_clu)
    return per_ave