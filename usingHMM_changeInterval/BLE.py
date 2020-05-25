#BLE commnication
import const
from func import calc_dist, Fading, PL, dBmtotv, tvtodBm

#定数クラスの定義
const = const.Const()

#BLE通信を行う処理
#引数 : ノードリスト, APリスト, 送信状態のノードインデックス
#戻り値 ： 送信パケット成功数
def BLEcomm(node_list, ap_list, index_list):

    arrival_packet = 0

    #パケット送信
    for ap in ap_list:
        #map_size = len(ap.map)
        for i in index_list:

            #距離計算（抽出）
            #tmp = [j for j in range(map_size) \
            #    if ap.map[j][0:2] == (node_list[i].x, node_list[i].y)]
            #tmp = tmp[0]

            #ap.rpow[i] = node_list[i].tpow - PL(node_list[i].freq, ap.map[tmp][2])\
            #        + ap.map[tmp][3] + Fading(node_list[i].speed, node_list[i].freq)

            #if node_list[i].packet <= 0:
            node_list[i].tosleep()
            #-----------デバック-------------#
            #print("----------node status---------")
            #node_l[i].output()
            #-------------------------------#


    #APによる受信処理
    #for ap in ap_list:
        #for i in index_list:
        #    SINR = 0.0
        #    tmp1 = dBmtotv(const.AWGN)
        #    tmp2 = dBmtotv(const.AWGN)
        #    for j in index_list:
        #        if i == j:
        #            tmp1 = dBmtotv(ap.rpow[i])
        #        elif i != j and node_list[i].sf == node_list[j].sf:
        #            tmp2 += dBmtotv(ap.rpow[j])

        #    SINR = tvtodBm(tmp1/tmp2)
        #    if SINR > const.SNR[node_list[i].sf] and \
        #        tvtodBm(tmp1) >= const.SENSING_LEVEL[node_list[i].sf]:

        #        node_list[i].packet -= node_list[i].rate * const.TIMEPERFLAME
        #        if node_list[i].packet <= 0:
    arrival_packet += 1

    return arrival_packet

#BLE ADV処理
#引数 : ノードリスト, APリスト, スリープ状態のノードインデックス
#戻り値 ： ADVを送信した回数
def BLEadv(node_list, ap_list, index_list):
    
    num_adv = 0
    
    #BLEによるWAIT処理
    for i in index_list:
        #node_list[i].timecount += 1
        #if node_list[i].timecount % const.ADV_INTERVAL == 0 :
        num_adv += 1
    
    return num_adv
