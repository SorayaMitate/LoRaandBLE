#データに関するあれこれを行う処理

import csv
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import const
from func import calc_dist, tvtodBm, dBmtotv, PL, lora_ber_Raylgh

const = const.Const()

#各種ファイル読み込み
path = '/home/owner/mitate/MieSCOPE/data/usingHMM/'
df = pd.read_csv(path + 'trajectory.csv', index_col=0)
HiddenModel = np.loadtxt(path + 'TransProb_matrix.txt')
ObservedModel = pd.read_csv(path + 'observationModel.csv',index_col=0)
CLU_LIST = list(df['cluNum'].unique())
CLU_LIST.remove(-1)
print('CLU_LIST =', CLU_LIST)


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
#出力 : クラスタNo(value値)
def randomCluNum():
    return random.choice(CLU_LIST)

#クラスタリストの出力
def out_clulist():
    return CLU_LIST

#総クラスタ数の出力
#出力 : クラスタ数
def numCluster():
    return len(CLU_LIST)

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
#出力 : クラスタのメッシュ座標
def CluNumtoPosi(cluNum):
    x_tmp = float(df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lat'])
    y_tmp = float(df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lon'])
    for i in range(const.A, const.B+const.DELTA_MESH, const.DELTA_MESH):
        
        if (i <= x_tmp) and (x_tmp < i+const.DELTA_MESH):
            x = int(i)
        else:
            pass
        
        if (i <= y_tmp) and (y_tmp < i+const.DELTA_MESH):
            y = int(i)
        else:
            pass
    
    #デバック
    #print('xtmp =', x_tmp)
    #print('ytmp =', y_tmp)
    #print('x=', x)
    #print('y =', y)

    return x,y

def return_perAvg(cluNum):
    for i, v in ObservedModel[ObservedModel['cluNum']==int(cluNum)].iterrows():
        tmp = v['per_avg']
        break
    return tmp

#BLE通信の遅延計算
#入力：Cluster No., BLE APリスト
#出力：遅延時間(期待値)
def calc_forble(node, ble_ap_list):
    
    #-------デバック-------
    print('node.cluNum =',node.cluNum)
    print('type(node.cluNum) =', type(node.cluNum))
    print('type(CLU_LIST) =', CLU_LIST[0])
    #---------------------

    index_cluNum = CLU_LIST.index(node.cluNum)
    size = HiddenModel[index_cluNum].shape[0]
    
    #遷移の可能性があるクラスタ群の抽出
    h = [(node.cluNum, HiddenModel[index_cluNum][i]) \
        for i in range(size) if HiddenModel[index_cluNum][i] > 0.0]

    ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]

    #遷移先毎の遅延時間と消費電流の期待値を算出
    #遷移先クラスタでループ
    delay_ave = 0.0
    energy_ave = 0.0
    delay = 0.0
    energy = 0.0

    for value in h:
        #delay = 0.0
        #energy = 0.0

        #遷移先クラスタにBLE APが存在する場合 : 遅延時間 = 移動距離
        # 遷移先に存在しない場合 : 遅延時間 = 移動距離 + 拡散率12のパケット送信時間
        if value[0] in ble_cluNum_list:
            addDelay = 0.0
            addEnrgy = 0.0
        else :
            addDelay = const.PACKET/const.RATE[const.SF12]
            addEnrgy = const.CURRENT[const.SF12]

        #遷移可能性のあるメッシュへの距離とメッシュへの遷移確率をリスト内タプルとして出力
        #tomesh = ([遷移確率, 現在位置からの距離])
        tomesh = []
        for i in ObservedModel[ObservedModel['cluNum']==int(value[0])].index:
            xtmp = ObservedModel.at[i,'lat']
            ytmp = ObservedModel.at[i,'lon']
            dist_tmp = calc_dist(xtmp, ytmp, node.x, node.y)
            tomesh.append((ObservedModel.at[i,'trans_prob'], dist_tmp))

        leng = len(tomesh)
        if leng > 0:
            #各メッシュ毎のPERを算出
            #ただし, PERがMIN_PERより小さい場合, MIN_PERを用いる
            for i in range(leng):
                if  const.PACKET_INTERVAL < tomesh[i][1]:
                    delay += tomesh[i][0] * (tomesh[i][1]+ addDelay - const.PACKET_INTERVAL) * value[1] 
                    energy += tomesh[i][0] * (const.BLE_CURRENT['IDLE'] * (tomesh[i][1] - const.PACKET_INTERVAL)\
                         + addEnrgy) * value[1]
                else :
                    delay += tomesh[i][0] * (1.0+ addDelay) * value[1]
                    energy += tomesh[i][0] * (const.BLE_CURRENT['IDLE'] + addEnrgy)\
                         * value[1]

            #delay_ave += delay / leng
            #energy_ave += energy / leng

        else: 
            pass

    #delay_ave = delay_ave / len(value)
    #energy_ave = energy_ave / len(value)

    return delay, energy

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
                    tmp = lora_ber_Raylgh(sf, snr)
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
                    area.at[i,'shadowing_avg'] = tmp
            else:
                pass

    return area
