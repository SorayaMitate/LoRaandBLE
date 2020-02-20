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

#自作モジュール
import Node 
import const 
import Result

#---------変数定義--------#
NUM_CORE = 1 #使用するコア数(メインプロセスは含まない)
ITERATION = 1
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
                    if k == 'node':
                        results[i].result_ave[k] = v
                        results_utility[i][k] = v
                    elif k == 'utility':
                        for k2, v2 in v.items():
                            results_utility[i][k2] += v2
                    else:
                        results[i].result_ave[k] += v

                j += 1
                if j == NUM_CORE:
                    break

        [p.join() for p in p_list]
        q.close()

        for k, v in results[i].result_ave.items():
            if k == 'node':
                pass
            else:
                v = v / float(NUM_CORE)

        for k, v in results_utility[i].items():
            if k == 'node':
                pass
            else:
                v = v / float(NUM_CORE)

    #ファイル出力処理
    path = os.getcwd()
    file_list = glob.glob(path + '\\*')
    if (path + '\\results') in file_list:
        pass
    else:
        os.mkdir(path + '\\results')
    
    path = path + '\\results'
    file_list = glob.glob(path)
    
    file_name = path + '\\Varrious_results.csv'
    if file_name in file_list:
        os.remove(file_name)
    keys = list(results[0].result_ave.keys())
    with open(file_name, 'w', newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        for result in results:
            writer.writerow(result.result_ave)

    file_name = path + '\\Utility_results.csv'
    if file_name in file_list:
        os.remove(file_name)
    keys = list(results_utility[0].keys())
    with open(file_name, 'w', newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        for result in results_utility:
            writer.writerow(result)

if __name__ == "__main__":
    main()  
        
