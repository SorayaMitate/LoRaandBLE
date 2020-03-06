import csv
import os
from math import pi, log10, sqrt, exp, cos
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque
from sympy import *

#自作モジュール
import Node
import const 
import Result
from func import *
from LoRa import *
from BLE import *
from AHP import *
from select_system import *

const = Const()

#入力：アプリケーション要求(タプル)
def comm(NUM_NODE,app,area,queue):

    #ランダムシードをプロセスIDで初期化
    random.seed(os.getpid()%10)

    results = Result.Result()

    #area = pd.read_csv('SC_shadowing.csv',index_col=0)

    #AHPで使用する用
    #1パケット当たりの電流
    ahp_current = {const.SF7:1.42, const.SF8:2.48, const.SF10:7.9, \
        const.SF11:14.4, const.SF12:26.8, const.BLE:0.0}
    #Delay
    ahp_delay = {const.SF7:const.PACKET/const.RATE[const.SF7], \
        const.SF8:const.PACKET/const.RATE[const.SF8], \
        const.SF10:const.PACKET/const.RATE[const.SF10], \
        const.SF11:const.PACKET/const.RATE[const.SF11], \
        const.SF12:const.PACKET/const.RATE[const.SF12], \
        const.BLE:0.0}
    
    #SNR-PERfuncの読み込み
    file_name = 'param.csv'
    with open(file_name) as f:
        reader = csv.reader(f)
        for row in reader:
            tmp_list = []
            for i in range(len(row)):
                if i == 0:
                    tmp = int(row[i])
                else:
                    tmp_list.append(float(row[i]))
            const.PARAM[tmp] = tmp_list

    for ite in range(const.ITERATION):

        results.clear()
        
        Node()
        #ノードとアクセスポイントの初期化
        node_list = [Agent(1) for i in range(NUM_NODE)]
        ap_list = [AP() for i in range(const.AP_MAX)]
        ble_ap_list = [AP() for i in range(const.BLE_AP_NUM)]

        #APの位置定義
        for ap in ap_list:
            ap.x = int(const.B / 2)
            ap.y = int(const.B / 2)

        for ap in ble_ap_list:
            #メッシュの作成
            #ap.map = [(i, j, calc_dist(ap.x, ap.y, i, j), Shadowing())\
            #    for i in range(const.A,const.B+1) for j in range(const.A, const.B+1) \
            #        if sqrt((ap.x-i)**2+(ap.y-j)**2) <= 200]
            ap.cluNum = randomCluNum()
            ap.x, ap.y = CluNumtoPosi(ap.cluNum)

        #ノードの状態、モード設定
        for node in node_list:
            #アプリケーション要求の定義
            node.qos_matrix = app[1]
            node.mode_tmp = const.WAIT
            node.state_tmp = const.SLEEP
            node.sf_tmp = const.SF7
            #node.output()
 
        #APの状態定義
        for ap in ap_list:
            ap.mode_tmp = const.WAIT
            ap.state_tmp = const.DATA_R

        #BLE APの状態定義
        for ap in ble_ap_list:
            ap.mode_tmp = const.WAIT
            ap.state_tmp = const.DATA_R

        #-----デバック-----#
        #print('node list len =',len(node_l))
        #print('AP list len =',len(ap_l))
        #-----------------#

        #エリアの定義area('lat','lon','shadowing','pathloss','cluNum','shadowing_avg')
        #pl = pd.Series([PL(const.FC, calc_dist(row['X'],row['Y'],ap_list[0].x,ap_list[0].y))\
        #    for i,row in area.iterrows()],name='PL')
        #area = pd.concat([area,pl],axis=1)
        #area['cluNum'] = -1
        #area['shadowing_avg'] = 0.0
        #area = calc_shadowingavg(area)
        #area.to_csv('sample.csv')

        traj_list = randomTraj()
        print('trajectory =',traj_list)
        traj_len = len(traj_list)*2

        for flame in range(traj_len):
            
            #ノードの状態変更と移動
            for node in node_list:
                #node.run()
                node.mode = node.mode_tmp
                node.state = node.state_tmp
                node.sf = node.sf_tmp
                node.rate = const.RATE[node.sf]

                if flame % 2 == 0:
                    #Nodeの遷移
                    #clusterNo.はクラスタ番号からインデックスへ変更
                    node.cluNum = convertIndex(traj_list.pop(0))
                    node.x, node.y = CluNumtoPosi(node.cluNum)

                    #使用可能拡散率の選定(現在の位置から)
                    dist_tmp = float(calc_dist(node.x, node.y, ap_list[0].x, ap_list[0].y))

                    #ネットワーク実測値の計算
                    ahp_current[const.BLE] = calc_energy_ble(node.cluNum, ble_ap_list,ahp_current[const.SF12])
                    ahp_current_norm = ahp_normrize(ahp_current)
                    ahp_delay[const.BLE] = calc_delay_ble(node.cluNum, ble_ap_list)
                    ahp_delay_norm = ahp_normrize(ahp_delay)
                    ahp_per = calc_per(node.cluNum, area, const.PARAM)
                    ahp_per_norm = ahp_normrize(ahp_per)
                    #AHP計算とシステム選択
                    systemlist = [system for system in const.SYSTEM_LIST if ahp_per[system] <= const.PER_THRESHOLD]
                    node.sf_tmp = AdaptionAlgorithm_AHP(systemlist, node.qos_matrix,\
                        ahp_current_norm, ahp_delay_norm, ahp_per_norm)

                    results.energy += dist_tmp / node.speed * const.BLE_CURRENT['IDLE']

                    #utilityのカウント
                    #clu_systemにはシステムインデクスを格納
                    results.clu_system.append(node.sf_tmp)
                    results.shadowing_avg.append(area[area['cluNum']==int(convertClusterNO(node.cluNum))]\
                        ['shadowing_avg'].mode()[0])
                    results.dist.append(dist_tmp)

                    #print('--------- node cluster = ' + str(node.cluNum) + '----------')
                    #print('dist = ',dist_tmp)
                    #print('current = ',ahp_current)
                    #print('current norm = ',ahp_current_norm)
                    #print('delay = ',ahp_delay)
                    #print('delay norm = ',ahp_delay_norm)
                    #print('per =',ahp_per)
                    #print('per norm= ',ahp_per_norm)
                    #print('system list =',systemlist)
                    #print('node.sf_tmp',node.sf_tmp)

                else :
                    pass

            #APの状態変更
            for ap in ap_list:
                ap.mode = ap.mode_tmp
                ap.state = ap.state_tmp
                ap.rpow = [const.AWGN] * NUM_NODE

            for ap in ble_ap_list:
                ap.mode = ap.mode_tmp
                ap.state = ap.state_tmp
                ap.rpow = [const.AWGN] * NUM_NODE

            #パケット生起
            for node in node_list:
            #    if float(flame) >= node.interval and ( node.state == const.SLEEP
            #        or node.state == const.BLE_SLEEP or node.state == const.BLE_ADV): 
                if flame % 2 == 0:
                    if node.sf_tmp == const.BLE:
                        node.toBLE_DATA_T()
                    else:
                        node.toDATA_T()
                    results.packet_occur += 1
                else:
                    pass

            #LoRa通信処理
            tx_index = [i for i in range(NUM_NODE) if node_list[i].state == const.DATA_T]
            if len(tx_index) != 0:
                results.packet_arrival += LoRa_comm(node_list, ap_list, tx_index)

            #BLE通信処理
            ble_tx_index = [i for i in range(NUM_NODE) if node_list[i].state == const.BLE_DATA_T]
            if len(ble_tx_index) != 0:
                results.packet_arrival += BLEcomm(node_list, ble_ap_list, ble_tx_index)

            #BLE ADV処理
            ble_adv_index = [i for i in range(NUM_NODE) if node_list[i].state == const.BLE_ADV]
            if len(ble_adv_index) != 0:
                results.packet_arrival += BLEcomm(node_list, ble_ap_list, ble_adv_index)
            
        #results.output()
        results.sum()

    result = results.average(const.ITERATION, app[0])
    queue.put(result)
