# coding: UTF-8

'''
Data : 2020/2/5
Name : Soraya Mitate
#comm()の入力：iTERATRION, NODE, Queue
#comm()の出力(辞書)：{'occur':**, 'arrival':**, 'energy':**, 'PER':**}
'''

import csv
from comm import *
import multiprocessing as mp
import os
import glob
import pandas as pd

#自作モジュール
import Node 
import const 
import Result

NUM_CORE = 4 #使用するコア数(メインプロセスは含まない)

#定数クラスの定義
const = Const()

def main():

    for sf in const.SF_LIST:
        list_per = []
        list_snr = []
        
        for ite in range(const.ITERATION):
            q = mp.Queue()
            p_list = [mp.Process(target=comm, args=(const.NODE_MIN, sf, q,)) \
                for j in range(NUM_CORE)]
            [p.start() for p in p_list]

            j=0
            while True:
                if q.empty() is False:
                    tmp = q.get()
                    list_per = list_per + tmp['PER']
                    list_snr = list_snr + tmp['SNR']

                    j += 1
                    if j == NUM_CORE:
                        break

            [p.join() for p in p_list]
            #[p.close() for p in p_list]
            q.close()

        snr = pd.Series(list_snr,name='SNR')
        per = pd.Series(list_per,name='PER')

        data = pd.concat([snr, per],axis=1)

        file_name = str(sf) + '_results.csv'
        data.to_csv(file_name)

if __name__ == "__main__":
    main()  
        
