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

#---------変数定義--------#
NUM_CORE = 1 #使用するコア数(メインプロセスは含まない)
ITERATION = 5
#------------------------#

#定数クラスの定義
const = Const()

def main():

    node_list = [i for i in range(const.NODE_MIN, const.NODE_MAX, const.DELTA_NODE)]
    len_node_list = len(node_list)

    #node = [i for i in range(NODE_MIN, NODE_MAX, DELTA_NUM)]
    results = [Result.Result() for i in range(len_node_list)]
    results_utility = [{'node':0, const.SF7:0.0, const.SF8:0.0, const.SF10:0.0, \
        const.SF11:0.0, const.SF12:0.0, const.BLE:0.0} for i in range(len(node_list))]
    results_system = {'clu_system':[], 'shadowing_avg':[], 'dist':[]}

    for i in range(len_node_list):

        q = mp.Queue()
        p_list = [mp.Process(target=comm, args=(ITERATION, node_list[i], q,)) \
            for j in range(NUM_CORE)]
        [p.start() for p in p_list]

        j=0
        while True:
            if q.empty() is False:
                tmp = q.get()
                for k, v in tmp.items():
                    if k == 'clu_system':
                        results_system[k] += v
                    elif k == 'shadowing_avg':
                        results_system[k] += v
                    elif k == 'dist':
                        results_system[k] += v
                    else :
                        pass

                j += 1
                if j == NUM_CORE:
                    break

        [p.join() for p in p_list]
        q.close()

    #ファイル出力処理
    file_name = 'system_results.csv'
    df = pd.DataFrame({
        'clu_system':results_system['clu_system'],
        'shadowing_avg':results_system['shadowing_avg'],
        'dist':results_system['dist']
    })
    print(df)
    df.to_csv(file_name)

if __name__ == "__main__":
    main()  
        
