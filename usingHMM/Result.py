import pandas as pd

from const import *

const = Const()        

class Result():
    def __init__(self):
        self.packet_occur = 0
        self.packet_arrival = 0
        self.energy = 0.0
        self.result_ave = {'node':0, 'occur':0.0, 'arrival':0.0, 'PER':0.0,\
            'energy':0.0, 'utility':0.0}
        self.utiity_ave = {const.SF7:0.0, const.SF8:0.0, const.SF10:0.0,\
            const.SF11:0.0, const.SF12:0.0, const.BLE:0.0}
        self.utiity = {const.SF7:0, const.SF8:0, const.SF10:0, \
            const.SF11:0, const.SF12:0, const.BLE:0}
        
        #クラスタのPER平均毎のシステム選択割合
        #self.clu_system = pd.DataFrame(0, index=const.PER_AVG, columns=const.SYSTEM_LIST)
        #self.clu_system_avg = pd.DataFrame(0.0, index=const.PER_AVG, columns=const.SYSTEM_LIST)
        self.clu_system = []
        self.shadowing_avg = []
        self.dist = []
    
    def clear(self):
        self.packet_occur = 0
        self.packet_arrival = 0
        self.energy = 0.0
        for system in const.SYSTEM_LIST:
            self.utiity[system] = 0

    def output(self, node_num):
        print('packet occur =', self.packet_occur)
        print('packet arrival =', self.packet_arrival)
        print('energy =', self.energy)

    def sum(self, node_num):
        self.result_ave['occur'] += self.packet_occur
        self.result_ave['arrival'] += self.packet_arrival
        self.result_ave['energy'] += self.energy
        #utilityの計算
        for system in const.SYSTEM_LIST:
            self.utiity_ave[system] += float(self.utiity[system]) / float(node_num) \
                / float(const.TIME_MAX) 

    def average(self, ite, num_node):
        self.result_ave['node'] = num_node
        self.result_ave['occur'] = float(self.result_ave['occur']) / float(ite)
        self.result_ave['arrival'] = float(self.result_ave['arrival']) / float(ite)
        self.result_ave['PER'] = self.result_ave['arrival'] / self.result_ave['occur']
        self.result_ave['energy'] = float(self.result_ave['energy']) / float(ite)
        for system in const.SYSTEM_LIST:
            self.utiity_ave[system] = self.utiity_ave[system] / float(ite)
        self.result_ave['utility'] = self.utiity_ave
        self.result_ave['clu_system'] = self.clu_system
        self.result_ave['shadowing_avg'] = self.shadowing_avg
        self.result_ave['dist'] = self.dist
        return self.result_ave
    
