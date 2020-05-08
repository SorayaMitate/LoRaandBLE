'''
Data : 2020/2/5
Name : Soraya Mitate
#comm()の入力：iTERATRION, NODE, Queue
#comm()の出力(辞書)：{'occur':**, 'arrival':**, 'energy':**, 'PER':**}
'''

import csv
import multiprocessing as mp
import os
import glob
import pandas as pd

#自作モジュール
import const 
import Result
from comm import comm

#---------変数定義--------#
NUM_CORE = 1 #使用するコア数(メインプロセスは含まない)
#------------------------#

#定数クラスの定義
const = const.Const()

def main():

    #path = '/home/owner/mitate/MieSCOPE/LoRaandBLE/results/'
    path = '/home/flab/mitate/LoRaandBLE/usingHMM/result/'

    #エリアの定義
    #area = SpacialColShadowing(const.DELTA_MESH, const.B, const.B, const.SHADOWING_VAR, const.D_COR)
    area = pd.read_csv('area.csv')

    results = Result.Result()
    df_results = pd.DataFrame(results.result_ave.values(), \
        index=results.result_ave.keys()).T

    for qos in const.app.items():

        print('QOS Matrix= ', qos)

        for k,v in results.result_ave.items():
            results.result_ave[k] = 0.0

        q = mp.Queue()
        p_list = [mp.Process(target=comm, args=(const.NODE_MIN,qos,area,q,)) \
            for j in range(NUM_CORE)]
        [p.start() for p in p_list]

        j=0
        while True:
            if q.empty() is False:
                tmp = q.get()
                for k, v in tmp.items():
                    if isinstance(v, str) == True:
                        results.result_ave[k] = v
                    elif k == 'system':
                        print('k = ', k)
                        print('v = ', v)
                    else:
                        results.result_ave[k] += v

                j += 1
                if j == NUM_CORE:
                    break

        [p.join() for p in p_list]
        q.close()

        for k, v in results.result_ave.items():
            if isinstance(v, str) == False:
                results.result_ave[k] = results.result_ave[k] / float(NUM_CORE)

        print('qos =',qos)
        print('results.result_ave',results.result_ave)

        tmp = pd.DataFrame(results.result_ave.values(), \
            index=results.result_ave.keys()).T
        df_results = df_results.append(tmp, ignore_index = True)

    file_name = path + 'results.csv'
    df_results.to_csv(file_name)

if __name__ == "__main__":
    main()  
        
