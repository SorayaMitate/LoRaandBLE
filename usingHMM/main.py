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
from Result import *

#---------変数定義--------#
NUM_CORE = 4 #使用するコア数(メインプロセスは含まない)
#------------------------#

#定数クラスの定義
const = Const()

def main():

    path = '/home/owner/mitate/MieSCOPE/LoRaandBLE/results/'

    area = pd.read_csv('sample.csv',index_col=0)

    results = Result()
    df_results = pd.DataFrame(results.result_ave.values(), \
        index=results.result_ave.keys()).T

    for qos in const.app.items():
    
        for k,v in results.result_ave.items():
            results.result_ave[k] = 0.0
        results_system = {'clu_system':[], 'shadowing_avg':[], 'dist':[]}

        q = mp.Queue()
        p_list = [mp.Process(target=comm, args=(const.NODE_MIN,qos,area,q,)) \
            for j in range(NUM_CORE)]
        [p.start() for p in p_list]

        j=0
        while True:
            if q.empty() is False:
                tmp = q.get()
                for k, v in tmp.items():
                    if isinstance(v, list) == True:
                        results_system[k] += v
                    else :
                        if isinstance(v, str) == True:
                            results.result_ave[k] = v
                        else:
                            results.result_ave[k] += v

                print('qos =',qos)
                print('results.result_ave',results.result_ave)

                j += 1
                if j == NUM_CORE:
                    break

        [p.join() for p in p_list]
        q.close()

        for k, v in results.result_ave.items():
            if isinstance(v, str) == False:
                results.result_ave[k] = results.result_ave[k] / float(NUM_CORE)
        
        tmp = pd.DataFrame(results.result_ave.values(), \
            index=results.result_ave.keys()).T
        df_results = df_results.append(tmp, ignore_index = True)

        #ファイル出力処理
        file_name = path + qos[0] + 'system_results.csv'
        df = pd.DataFrame({
            'clu_system':results_system['clu_system'],
            'shadowing_avg':results_system['shadowing_avg'],
            'dist':results_system['dist']
        })
        df.to_csv(file_name)

    file_name = path + 'results.csv'
    df_results.to_csv(file_name)

if __name__ == "__main__":
    main()  
        
