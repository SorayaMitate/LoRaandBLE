import random
import numpy as np
from collections import deque
from sympy import * 

from func import*
from const import *

const = Const()

class Node():
    #ノードの設定
    def __init__(self):
        self.x = random.randint(const.A,const.B)
        self.y = random.randint(const.A,const.B)
        self.tpow = const.TPOW
        self.freq = const.FC
        self.sf = 0
        self.sf_tmp = 0
        self.rate = 0.0
        self.buffer = deque()
        self.packet = 0
        self.timecount = 0
        self.fading_tmp = 0.0 #1パケット受信間のフェージング値の固定を保証
        self.interval = poisson()
        self.mode = -1
        self.mode_tmp = -1
        self.state = -1
        self.state_tmp = -1

        #cluster Noの格納
        self.cluNum = -1

        #使用可能システムリスト
        self.system_list = []
    
    def tosleep(self):
        self.buffer.clear()
        self.packet = 0
        self.mode_tmp = const.WAIT
        self.state_tmp = const.SLEEP
        self.interval += const.DC[self.sf] + poisson() 

    def toDATA_T(self):
        self.buffer.appendleft(1)
        self.packet = const.PACKET
        self.mode_tmp = const.ACTIVE
        self.state_tmp = const.DATA_T

    def toBLE_ADV(self):
        self.timecount = 0
        self.packet = 0
        self.mode_tmp = const.WAIT
        self.state_tmp = const.BLE_ADV

    def toBLE_DATA_T(self):
        self.packet = const.PACKET
        self.mode_tmp = const.ACTIVE
        self.state_tmp = const.BLE_DATA_T

    def BLE_occur_packet(self):
        self.buffer.appendleft(1)
        self.interval += const.DC[self.sf] + poisson()


    def output(self):
        #デバック用
        print('Node position x =',self.x)
        print('Node position y =',self.y)
        print('buffer =', self.buffer)
        print('packet =', self.packet)
        print('mode_tmp =', self.mode_tmp)
        print('state_tmp =', self.state_tmp)
        print('mode =', self.mode)
        print('state =', self.state)
        print('interval =', self.interval)
        print('SF =',self.sf)
        print('Data Rate =',self.rate)
        #print('Duty Cycle =',const.DC[self.sf])

class Agent(Node):
    #移動ノードの設定(固定ノードの継承)
    def __init__(self, ahp_qos):
        super(Agent, self).__init__() #Nodeのメンバ変数ごと継承
        self.buffer = deque(maxlen=const.BUFFER_SIZE)
        self.speed = const.SPEED
        self.qos_matrix = Matrix([[1, ahp_qos],[1/ahp_qos,1]])

    def run(self):
        #agentがエリア端に到着した時、走行距離を初期化し
        #ノード位置を初期化しランダムに移動
        if self.x >= const.B:
            self.x = 0.0
            #self.y = random.randint(A,B)
        self.x += self.speed * float(const.TIMEPERFLAME)

class AP(Node):
    def __init__(self):
        super(AP, self).__init__() #ノードのメンバ変数ごと継承
        self.x = 0.0 #論文に従う
        self.dist = [0.0] * const.NODE_MAX #ndarrayと悩む
        self.rpow = [0.0] * const.NODE_MAX 
        self.node_num = {const.SF7:0, const.SF8:0, const.SF10:0, \
            const.SF11:0, const.SF12:0, const.BLE:0} #各拡散率のノード数を格納
        self.sensing_level = 0.0
        #self.sinr = 0.0
