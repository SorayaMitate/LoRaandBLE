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
df = pd.read_csv(path + 'trajectory.csv', index_col=0)
HiddenModel = np.loadtxt(path + 'TransProb_matrix.txt')
ObservedModel = pd.read_csv(path + 'observationModel.csv',index_col=0)
CLU_LIST = list(df['cluNum'].unique())

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

#クラスタNo.のランダム選択()
def randomCluNum():
    return random.choice(CLU_LIST)

#Trajectoryのランダム選択
#出力：Trajectoryリスト[クラスタNo....]
def randomTraj():
    while True:
        traj_list = []
        tra = random.choice(df['tra_num'].unique())
        df_tmp = df[df['tra_num']==tra]
        tmp = -1
        for cluNum in df_tmp['cluNum']:
            if tmp != cluNum:
                traj_list.append(cluNum)
                tmp = cluNum
            else:
                pass
        if len(traj_list) > 1:
            break
        else:
            pass
    return traj_list

#クラスタ番号⇒クラスタのxy座標
def CluNumtoPosi(cluNum):
    x_tmp = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lat']
    y_tmp = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lon']
    for i in range(const.A, const.B, const.DELTA_MESH):
        if (i <= x_tmp) and (x_tmp < i+const.DELTA_MESH):
            x = int(i)
        elif (i <= y_tmp) and (y_tmp < i+const.DELTA_MESH):
            y = int(i)
        else:
            pass
    return x,y

def return_perAvg(cluNum):
    for i, v in ObservedModel[ObservedModel['cluNum']==int(cluNum)].iterrows():
        tmp = v['per_avg']
        break
    return tmp

#BLE通信の遅延計算
#入力：Cluster No., BLE APリスト
#出力：遅延時間(期待値)
def calc_delay_ble(cluNum, ble_ap_list,interval):

    #cluNumをインデックスへ変換
    cluNum = CLU_LIST.index(cluNum)

    size = HiddenModel[cluNum].shape[0]
    l = [i for i in range(size) if HiddenModel[cluNum][i] > 0.0]

    tmp = [HiddenModel[cluNum][i] for i in range(size) if HiddenModel[cluNum][i] > 0.0]

    ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]
    x1, y1 = CluNumtoPosi(cluNum)
    delay = 0.0
    for i in l:
        x2, y2 = CluNumtoPosi(i)
        dist_tmp = calc_dist(x1,y1,x2,y2)-interval
        if dist_tmp < 1.0:
            dist_tmp = 1.0
        else:
            pass

        if (i in ble_cluNum_list) == True:
            delay += HiddenModel[cluNum][i] * dist_tmp
        else:
            delay += HiddenModel[cluNum][i] * dist_tmp + const.PACKET/const.RATE[const.SF12]
    return delay

#BLE通信の消費電流の計算
#入力：Cluster No., BLE APリスト, BLEの電流
#出力：消費電流(期待値)
def calc_energy_ble(cluNum, ble_ap_list, e_sf12, interval):
    size = HiddenModel[cluNum].shape[0]
    l = [i for i in range(size) if HiddenModel[cluNum][i] > 0.0]
    ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]
    x1, y1 = CluNumtoPosi(cluNum)
    delay = 0.0
    for i in l:

        x2, y2 = CluNumtoPosi(i)
        dist_tmp = calc_dist(x1,y1,x2,y2)-interval
        if dist_tmp < 1.0:
            dist_tmp = 1.0
        else:
            pass

        if (i in ble_cluNum_list) == True:
            delay += HiddenModel[cluNum][i] * (dist_tmp)*const.BLE_CURRENT['IDLE']
        else:
            delay += HiddenModel[cluNum][i] * dist_tmp*const.BLE_CURRENT['IDLE'] + e_sf12
    return delay

#各メッシュの遷移先からPERを算出する処理
#入力 : ノードのcluNNum, 対象エリア(DF), SNR-PER曲線(システムごとのparam)
def calc_per(node, ap, area):
    index_cluNum = CLU_LIST.index(node.cluNum)
    size = HiddenModel[index_cluNum].shape[0]
    
    #遷移の可能性があるクラスタ群の抽出
    h = [(node.cluNum, HiddenModel[index_cluNum][i]) \
        for i in range(size) if HiddenModel[index_cluNum][i] > 0.0]
    
    per = {system:0.0 for system in const.SF_LIST}
    per_ave = {system:0.0 for system in const.SF_LIST}

    #遷移先毎のperを算出
    #遷移先クラスタでループ
    for value in h:

        #遷移可能性のあるメッシュのシャドウイング値とメッシュへの遷移確率を
        # パスロス値をリスト内タプルとして出力
        tomesh = []
        for i in ObservedModel[ObservedModel['cluNum']==int(value[0])].index:
            xtmp = ObservedModel.at[i,'lat']
            ytmp = ObservedModel.at[i,'lon']
            dist_tmp = calc_dist(xtmp, ytmp, ap.x, ap.y)
            tomesh.append((area[(area['X']==xtmp)&(area['Y']==ytmp)]['SHADOWING'],\
                ObservedModel.at[i,'trans_prob'], PL(node.freq, dist_tmp)))

        leng = len(tomesh)
        if leng > 0:
            #各メッシュ毎のPERを算出
            #ただし, PERがMIN_PERより小さい場合, MIN_PERを用いる
            for i in range(leng):
                snr = tvtodBm(dBmtotv(tomesh[i][0]-tomesh[i][2]+const.TPOW)\
                    /dBmtotv(const.AWGN))
                for sf in const.SF_LIST:
                    #BERの計算
                    tmp = lora_ber(sf, snr)
                    #PERの計算
                    tmp = 1 - pow((1-tmp), const.PACKET)
                    if tmp < const.MIN_PER:
                        tmp = const.MIN_PER
                    per[sf] += value[1]*tomesh[i][1]*tmp

            for system in const.SF_LIST:            
                per_ave[system] += per[system]

        else:
            pass 

    for system in const.SF_LIST:
        per_ave[system] = per_ave[system] / len(h)

    per_ave[const.BLE] = const.MIN_PER
    return per_ave

#クラスタごとの平均シャドウィング値を算出するプログラム
#入力 : area('lat','lon','shadowing','pathloss','cluNum','shadowing_avg'), 
#用いるdata：observation('lat','lon','cluNum','counts',trans_prob),
def calc_shadowingavg(area):
    for v in ObservedModel['cluNum'].value_counts().index:
        if v == -1:
            pass
        else:   
            tmp = 0.0
            index_list = []
            for i, row in ObservedModel[ObservedModel['cluNum']==v].iterrows():
                if (row['lat'] < const.B) and (row['lon'] < const.B):
                    j = area[(area['X']==int(row['lat']))&\
                        (area['Y']==int(row['lon']))].index[0]
                    tmp += area.at[j,'SHADOWING']
                    area.at[j,'cluNum'] = int(v)
                    index_list.append(j)
                
            #クラスタ毎の平均shadowing値を算出
            if len(ObservedModel[ObservedModel['cluNum']==v]) > 0:
                tmp = tmp / len(ObservedModel[ObservedModel['cluNum']==v])
                for i in index_list:
                    area.at[i,'shadowing_avg']=tmp
            else:
                pass

    return area
