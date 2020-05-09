#変数定義ファイル

from sympy import Matrix

class Const():
    def __init__(self):
        #シミュレーション設定項目
        #self.TIME_MAX = 193750 #(3.1kmを走るのにかかる時間[sec] * 100)[*10msec]
        self.TIME_MAX = 200 #(3.1kmを走るのにかかる時間[sec] * 100)[*10msec]
        self.TIMEPERFLAME = 1 #1フレームの時間[1sec]
        self.ITERATION = 2
        self.NODE_MIN = 1
        self.NODE_MAX = 1
        self.DELTA_NODE = 1
        self.AP_MAX = 1
        self.BLE_AP_NUM = 0.3 #クラスター数×BLE_AP_NUM
        self.PACKET_INTERVAL = 100
        self.MIN_PER = pow(10,-3)

        #座標パラメータ
        self.A = 0
        self.B = 2000 #m
        self.DELTA_MESH = 10
        self.CLUSTER_SIZE = 100

        self.PER_THRESHOLD = 0.1

        #シャドウィングパラメータ
        self.D_COR = 30
        self.SHADOWING_VAR = 8.0

        #ノード状態（mode）
        self.ACTIVE = 0
        self.LISTEN = 1
        self.WAIT = 2

        #ノード状態（state）
        self.DATA_T = 0
        self.ACK_T = 1
        self.DATA_R = 2
        self.ACK_R = 3
        self.SLEEP = 4
        self.BLE_DATA_T = 5
        self.BLE_ADV = 6
        self.BLE_SLEEP = 7

        #AWGN(dBm)
        self.AWGN = -100.0

        #パケット長
        self.PACKET = 25 * 8

        #ノードの設定項目
        self.SPEED = 1 #2m/sec
        self.BUFFER_SIZE = 1

        #Loraの設定項目
        #参考資料の元, 送信出力は6dBmに固定
        #VDD = 3.3V 固定
        self.TPOW = 6 #dBm
        #LORA CURRENT CONSUMPTION [mA/10msec]
        self.CURRENT = {self.ACTIVE:38.9, self.LISTEN:2.8, self.WAIT:0.0016}
        self.FC = 868100000 #868.1MHz
        self.BANDWIDTH = 125 #kHz

        self.SF7 = 7
        self.SF8 = 8
        self.SF10 = 9
        self.SF11 = 10
        self.SF12 = 11
        self.BLE = 12
        #ランダムに選択用リスト
        self.SYSTEM_LIST = [self.SF7, self.SF8, self.SF10, self.SF11, self.SF12, self.BLE]
        self.SF_LIST = [self.SF7, self.SF8, self.SF10, self.SF11, self.SF12]
        #RATE[bits/10msec]
        self.RATE = {self.SF7:5470.0, self.SF8:3130.0, self.SF10:980.0, \
                self.SF11:540.0, self.SF12:290.0, self.BLE:0.0}
        #SENSING LEVEL
        self.SENSING_LEVEL = {self.SF7:-123.0, self.SF8:-126.0, self.SF10:-132.0,\
            self.SF11:-134.5, self.SF12:-136.0, self.BLE:0.0}
        #SNR
        self.SNR = {self.SF7:-6.0, self.SF8:-9.0, self.SF10:-12.0,\
            self.SF11:-15.0, self.SF12:-20.0, self.BLE:0.0}
        #Duty Cycle [/10msec]
        self.DC = {self.SF7:float((self.PACKET/self.RATE[self.SF7])/0.01-self.PACKET/self.RATE[self.SF7]), 
                self.SF8:float((self.PACKET/self.RATE[self.SF8])/0.01-self.PACKET/self.RATE[self.SF8]),
                self.SF10:float((self.PACKET/self.RATE[self.SF10])/0.01-self.PACKET/self.RATE[self.SF10]),
                self.SF11:float((self.PACKET/self.RATE[self.SF11])/0.01-self.PACKET/self.RATE[self.SF11]), 
                self.SF12:float((self.PACKET/self.RATE[self.SF12])/0.01-self.PACKET/self.RATE[self.SF12]),
                #BLEのduty cycleはsf10のものを使用する
                self.BLE:float((self.PACKET/self.RATE[self.SF10])/0.01-self.PACKET/self.RATE[self.SF10])}

        #QOS項目の期待値を格納するのはこの定義
        #1パケット当たりの電流
        self.CURRENT = {self.SF7:1.42, self.SF8:2.48, self.SF10:7.9, \
            self.SF11:14.4, self.SF12:26.8, self.BLE:0.0}
       
        #Delay
        self.DELAY = {self.SF7:self.PACKET/self.RATE[self.SF7], \
            self.SF8:self.PACKET/self.RATE[self.SF8], \
            self.SF10:self.PACKET/self.RATE[self.SF10], \
            self.SF11:self.PACKET/self.RATE[self.SF11], \
            self.SF12:self.PACKET/self.RATE[self.SF12], \
            self.BLE:0.0}

        
        self.PER = {self.SF7:0.0, self.SF8:0.0, self.SF10:0.0,\
            self.SF11:.0, self.SF12:0.0, self.BLE:0.0}

        #BLEの変数定義
        #BUFFER_SIZE = 10
        #BLEのデータレート : 1M[bit/s]
        self.BLE_RATE = 1000000.0
        #スレーブによるアドバタイズインターバル:0.5[sec]
        self.ADV_INTERVAL = 0.5 #500msec
        #アドバタイズパケットの長さ
        #ADOVERTISE_SIZE = 
        #BLEの消費電流[mAh/sez]
        #dutycycle10%で33mWの消費(マスタにーよるスキャン)
        self.BLE_CURRENT = {'ADV':0.067, 'IDLE':33.0 / 3.0 / 5.0} 
        #BLEの各パケット送受信にかかる長さ [sec/bit]
        self.BLE_LENGTH = {'TX':10.0**(-6), 'RX':10.0**(-6), 'TIFS':150.0**(-6)}

        def calc_ble_energy(packet_num):
            #print('TX =',BLE_CURRENT['TX']*float(packet_num-1)*BLE_LENGTH['TX']*(PACKET+4*8))
            #print('RX =',BLE_CURRENT['RX']*float(packet_num)*BLE_LENGTH['RX']*4*8)
            #print('TIFS =',BLE_CURRENT['TIFS']*float(2*packet_num-1)*BLE_LENGTH['TIFS'])

            return self.BLE_CURRENT['TX']*float(packet_num-1)*self.BLE_LENGTH['TX']*(self.PACKET+4*8) + \
                self.BLE_CURRENT['RX']*float(packet_num)*self.BLE_LENGTH['RX']*4*8 + \
                self.BLE_CURRENT['TIFS']*float(2*packet_num-1)*self.BLE_LENGTH['TIFS']

        QOS = 5
        self.APP = {'equal':Matrix([[1,1,1],[1,1,1],[1,1,1]]), \
            'energy':Matrix([[1,QOS,QOS],[1/QOS,1,1],[1/QOS,1,1]]),\
            'delay':Matrix([[1,1/QOS,1],[QOS,1,QOS],[1,1/QOS,1]]),\
            'per':Matrix([[1,1,1/QOS],[1,1,1/QOS],[1,QOS,QOS]])}
