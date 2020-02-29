import csv
from math import pi, log10, sqrt, exp, cos
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque
from sympy import *

#自作モジュール
from Node import *
import const 
import Result
from func import *
from LoRa import *

const = Const()

def comm(ITERATION, NUM_NODE, queue):

    results = Result.Result()

    for ite in range(ITERATION):
        
        Node()
        #ノードとアクセスポイントの初期化
        node_list = [Agent(1) for i in range(NUM_NODE)]
        ap_list = [AP() for i in range(const.AP_MAX)]
        ble_ap_list = [AP() for i in range(const.BLE_AP_NUM)]

        #APの位置定義
        for ap in ap_list:
            ap.x = int(const.A / 2)
            ap.y = int(const.B / 2)

        #ノードの状態、モード設定
        for node in node_list:
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

        for flame in range(const.TIME_MAX):
            
            #ノードの状態変更と移動
            for node in node_list:
                node.run()
                node.mode = node.mode_tmp
                node.state = node.state_tmp
                node.sf = node.sf_tmp
                node.rate = const.RATE[node.sf]

            #APの状態変更
            for ap in ap_list:
                ap.mode = ap.mode_tmp
                ap.state = ap.state_tmp
                ap.rpow = [const.AWGN] * NUM_NODE

            #パケット生起
            for node in node_list:
                node.toDATA_T()

            #LoRa通信処理
            tx_index = [i for i in range(NUM_NODE) if node_list[i].state == const.DATA_T]
            LoRa_comm(node_list, ap_list, tx_index)

            for node in node_list:
                if len(node.que_snr) == const.QUE_LENGTH:
                    results.list_per.append((float(const.QUE_LENGTH)-float(sum(node.que_per)))\
                        /len(node.que_per))
                    results.list_snr.append(sum(node.que_snr)\
                        /len(node.que_snr))
                    node.que_snr.clear()
                    node.que_per.clear()

    print('-------------Node ', end='')
    print(NUM_NODE, end='')
    print('-------------')
    results = results.out()
    queue.put(results)
