#LoRa communication

from func import *
from const import *

#定数クラス
const = Const()

#LoRa通信を行う処理
#引数 : ノードリスト, APリスト, 送信状態のノードインデックス
#戻り値 ： 送信パケット成功数
def LoRa_comm(node_list, ap_list, index_list, cluNum_list, area):
    
    arrival_packet = 0

    #パケット送信
    for ap in ap_list:
        for i in index_list:

            #距離計算（抽出）
            #tmp = [j for j in range(map_size) \
            #    if ap.map[j][0:2] == (node_list[i].x, node_list[i].y)]
            dist_tmp = calc_dist(node_list[i].x, node_list[i].y, ap.x, ap.y)
            print('x,y =',node_list[i].x,node_list[i].y)
            print('clu =',cluNum_list)
            print('area=',area[area['cluNum']==node_list[i].cluNum]['shadowing_avg'])
            ap.rpow[i] = node_list[i].tpow - PL(node_list[i].freq, dist_tmp)\
                    + Fading(node_list[i].speed, node_list[i].freq)\
                        +area[area['cluNum']==cluNum_list[i]]['SHADOWING']

            #-----------デバック-------------#
            #print("----------node status---------")
            #node_l[i].output()
            #print('dist =', dist_tmp)
            #print('ap_pow =', ap.rpow[i])
            #-------------------------------#

    #APによる受信処理
    for ap in ap_list:
        for i in index_list:
            SINR = 0.0
            tmp1 = dBmtotv(const.AWGN)
            tmp2 = dBmtotv(const.AWGN)
            for j in index_list:
                if i == j:
                    tmp1 = dBmtotv(ap.rpow[i])
                elif i != j and node_list[i].sf == node_list[j].sf:
                    tmp2 += dBmtotv(ap.rpow[j])

            SINR = tvtodBm(tmp1/tmp2)
            if SINR > const.SNR[node_list[i].sf] and \
                tvtodBm(tmp1) >= const.SENSING_LEVEL[node_list[i].sf]:

                node_list[i].packet -= node_list[i].rate * const.TIMEPERFLAME
                if node_list[i].packet <= 0:
                    arrival_packet += 1
                    node_list[i].tosleep()
    
    return arrival_packet
                    
