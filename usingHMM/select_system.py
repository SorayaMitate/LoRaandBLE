#データに関するあれこれを行う処理

import csv
import numpy as np
import pandas as pd
import random

from const import *
from func import *

#各種ファイル読み込み
path = 'home/owner/mitate/MieSCOPE/data/usingHMM/'
df = pd.read_csv(path + 'data/traj_2000.csv', index_col=0)
trans_prob_mat = np.loadtxt(path + 'data/TransProb_matrix.txt')
index_clusterNo_df = pd.read_csv(path + 'data/IndextoClusterNo_df.csv', index_col=0, \
    usecols=['indexName','ClusterNo'])
with open('path + data/Trajectory_list') as f:
    reader = csv.reader(f)
    traj_list = [row for row in reader]

#PER分布の作成
#are_of[,lat,lon,shadowing,cluNum,counts,trans_prob]
area_df = pd.read_csv(path + 'data/observationModel.csv',index_col=0)
leng = len(area_df)
per_list = [per_gaussian() for i in range(leng)]
per_df = pd.DataFrame(per_list, columns=['per'])
area_df = pd.concat([area_df, per_df], axis=1)

const = Const()

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

def calc_per(cluNum):
    size = trans_prob_mat[cluNum].shape[0]
    l = [(index_clusterNo_df.at[i,'ClusterNo'], trans_prob_mat[cluNum][i]) \
        for i in range(size) if trans_prob_mat[cluNum][i] > 0.0]
    per = 0.0
    for value in l:
        per_list = [area_df.at[i, 'trans_prob'] * value[1] \
            for i in area_df[area_df['cluNum']==int(value[0])].index]
        per += sum(per_list) / len(per_list)
    return per / len(l)