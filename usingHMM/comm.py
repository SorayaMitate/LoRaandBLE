import csv
import os
from math import pi, log10, sqrt, exp, cos
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque

#自作モジュール
import Node
import const 
import Result
import select_system as ss
from  func import calc_dist 
from LoRa import LoRa_comm 
from BLE import BLEcomm 
from AHP import adaptionAlgorithm, ahp_normrize

const = const.Const()

#入力：アプリケーション要求(タプル)
def comm(NUM_NODE,app,area,queue):

    #ランダムシードをプロセスIDで初期化
    random.seed(os.getpid())

    results = Result.Result()

    #BLEAP数の定義
    ble_ap_num = int(const.BLE_AP_NUM * ss.numCluster())
    #ble_ap_num = int(ss.numCluster()) -1#デバック用

    for ite in range(1,const.ITERATION+1):
        #print('iteration = ',ite)

        results.clear()
        
        Node.Node()
        #ノードとアクセスポイントの初期化
        node_list = [Node.Agent(1) for i in range(NUM_NODE)]
        ap_list = [Node.AP() for i in range(const.AP_MAX)]
        ble_ap_list = [Node.AP() for i in range(ble_ap_num)]

        #LoRa APの位置定義
        for ap in ap_list:
            ap.x = float(const.B / 2)
            ap.y = float(const.B / 2)

        #BLE APの位置定義(任意のクラスタへの割り当て)
        i=0
        for ap in ble_ap_list:
            ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]
            while True:
                tmp = ss.randomCluNum()
                if ((tmp in ble_cluNum_list)== False) \
                    and (tmp != const.BUG_CLUNUM):
                    i += 1
                    break
            ap.cluNum = tmp
            ap.x, ap.y = ss.CluNumtoPosi(ap.cluNum)
        ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]
        
        #------デバック用------
        #CLU_LIST = ss.out_clulist()
        #for ap in ble_ap_list:
        #    ap.cluNum = CLU_LIST.pop(0)
        #    ap.x, ap.y = ss.CluNumtoPosi(ap.cluNum)            
        #ble_cluNum_list = [ap.cluNum for ap in ble_ap_list]        
        #--------------------

        #ノードの状態、モード設定
        for node in node_list:
            #アプリケーション要求の定義
            node.qos_matrix = app[1]   #####main
            #node.qos_matrix = app       #####main2
            node.mode_tmp = const.WAIT
            node.state_tmp = const.SLEEP
            node.sf_tmp = const.SF7

            node.interval = const.PACKET_INTERVAL ##main
            #node.interval = INTERVAL   ###main2
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

        #1遷移で1パケット送信
        traj_list = ss.randomTraj()
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
                    #print('cluNum =',node.cluNum)
                    node.cluNum = traj_list.pop(0)
                    #print('after cluNum=',node.cluNum)

                    #遅延時間の計算
                    #print('before =', node.x, node.y)
                    #print('after =',CluNumtoPosi(node.cluNum))
                    #print('delay =', calc_dist(node.x, node.y,*CluNumtoPosi(node.cluNum)))
                    #現在の位置と遷移先クラスタの位置から遅延時間を計算
                    dist_tmp = calc_dist(node.x, node.y,*ss.CluNumtoPosi(node.cluNum))
                    delay_tmp = calc_dist(node.x, node.y,*ss.CluNumtoPosi(node.cluNum)) - const.PACKET_INTERVAL
                    if delay_tmp < 1.0:
                        delay_tmp = 1.0

                    #ノードの位置座標の更新
                    node.x, node.y = ss.CluNumtoPosi(node.cluNum)
                    dist_loraAP = calc_dist(node.x, node.y, ap_list[0].x, ap_list[0].y)

                    #QoS項目の期待値計算
                    const.DELAY[const.BLE], const.CURRENT[const.BLE] = ss.calc_forble(node_list[0], ble_ap_list)
                    per_list = ss.calc_per(node_list[0], ap_list[0], ble_ap_list, area)
                    #print('per_list =',per_list)

                    #PER閾値を満たさないシステムの除去
                    systemlist = [system for system in const.SYSTEM_LIST if per_list[system] <= const.PER_THRESHOLD]
                    if len(systemlist) ==0:
                        systemlist.append(const.BLE)
                    ahp_per = {}
                    ahp_delay = {}
                    ahp_current = {}
                    for system in systemlist:
                        ahp_per[system] = per_list[system]
                        ahp_delay[system] = const.DELAY[system]
                        ahp_current[system] = const.CURRENT[system]

                    ahp_per_norm = ahp_normrize(ahp_per)
                    ahp_delay_norm = ahp_normrize(ahp_delay)
                    ahp_current_norm = ahp_normrize(ahp_current)
                    
                    #AHP計算とシステム選択
                    node.sf_tmp = adaptionAlgorithm(systemlist, node.qos_matrix,\
                        ahp_current_norm, ahp_delay_norm, ahp_per_norm)

                    ######ランダムセレクト
                    #systemlist = const.SYSTEM_LIST
                    #node.sf_tmp = random.choice(systemlist)

                    #BLE通信時の結果格納
                    if node.sf_tmp == const.BLE:
                        results.delay += delay_tmp
                        results.energy += delay_tmp * const.BLE_CURRENT['IDLE']

                    #results.system[node.sf_tmp] += 1
                    results.dist.append(dist_loraAP)
                    results.dist_clu.append(dist_tmp)
                    results.system.append(node.sf_tmp)

                    #print('--------- node cluster = ' + str(node.cluNum) + '----------')
                    #print('dist_tmp bettween Cluster and LoRa AP =', dist_loraAP)
                    #print('dist_tmp bettween Cluster and Cluster =', dist_tmp)
                    #print('delay_tmp =',delay_tmp)
                    #print('current = ',const.CURRENT)
                    #print('current norm = ',ahp_current_norm)
                    #print('delay = ',const.DELAY)
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

            #BLE通信処理
            ble_index = [i for i in range(NUM_NODE) if (node_list[i].state == const.BLE_DATA_T)]
            ble_tx_index = []
            if len(ble_index) > 0:
                for i in ble_index:
                    if node_list[i].cluNum in ble_cluNum_list:
                        ble_tx_index.append(i)
                    else:
                        node_list[i].BLEtoSF12()
                        #print('change Node system')
                        #print('cluNum =',node_list[i].cluNum)
            if len(ble_tx_index) > 0:
                #print('use BLE')
                #print('cluNum =',node_list[0].cluNum)
                results.packet_arrival += BLEcomm(node_list, ble_ap_list, ble_tx_index)                

            #LoRa通信処理
            tx_index = [i for i in range(NUM_NODE) if node_list[i].state == const.DATA_T]
            if len(tx_index) != 0:
                #print('use Lora')
                #print('cluNum =',node_list[0].cluNum)
                results.packet_arrival += LoRa_comm(node_list, ap_list, tx_index, area)
                results.delay += const.DELAY[node.sf]
                results.energy += const.CURRENT[node.sf_tmp]

            #BLE ADV処理
            #ble_adv_index = [i for i in range(NUM_NODE) if node_list[i].state == const.BLE_ADV]
            #if len(ble_adv_index) != 0:
            #    results.packet_arrival += BLEcomm(node_list, ble_ap_list, ble_adv_index)
            
        #results.output()
        results.sum()

    result = results.average(const.ITERATION, app[0])
    #result = results.average(const.ITERATION, INTERVAL)

    #print('Packet occur =',results.result_ave['occur'])
    #print('Packet arrival =',results.result_ave['arrival'])
    #print('Packet Error Rate =',results.result_ave['PER'])
    queue.put(result)
