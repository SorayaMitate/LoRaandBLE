import pandas as pd

import const

const = const.Const()        

class Result():
    def __init__(self):
        self.packet_occur = 0
        self.packet_arrival = 0
        self.energy = 0.0
        self.delay = 0.0
        self.clu_system = []
        self.shadowing_avg = []
        self.dist = []
        self.result_ave = {'app':0, 'occur':0.0, 'arrival':0.0, 'PER':0.0,\
            'energy':0.0, 'delay':0.0, 'system':{}}
        self.system = {const.SF7:0, const.SF8:0, const.SF10:0,\
            const.SF11:0, const.SF12:0, const.BLE:0}
    
    def clear(self):
        self.packet_occur = 0
        self.packet_arrival = 0
        self.energy = 0.0

    def output(self):
        print('packet occur =', self.packet_occur)
        print('packet arrival =', self.packet_arrival)
        print('energy =', self.energy)
        print('delay =', self.delay)

    def sum(self):
        self.result_ave['occur'] += self.packet_occur
        self.result_ave['arrival'] += self.packet_arrival
        self.result_ave['energy'] += self.energy
        self.result_ave['delay'] += self.delay 

    #引数：アプリケーション要求(辞書)のキー
    def average(self, ite, app):
        self.result_ave['app'] = str(app)
        self.result_ave['occur'] = float(self.result_ave['occur']) / float(ite)
        self.result_ave['arrival'] = float(self.result_ave['arrival']) / float(ite)
        self.result_ave['PER'] = self.result_ave['arrival'] / self.result_ave['occur']
        self.result_ave['energy'] = float(self.result_ave['energy']) \
            / float(self.result_ave['arrival']) / float(ite)
        self.result_ave['delay'] = float(self.result_ave['delay']) \
            / float(self.result_ave['arrival']) / float(ite)
        tmp = sum( v for v in self.system.values())
        for k,v in self.system.items():
            self.result_ave['system'][k] = v / tmp

        return self.result_ave
    
