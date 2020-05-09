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
    df = pd.DataFrame(results.result_out.values(), \
        index=results.result_out.keys()).T

    for qos in const.APP.items():

        print('QOS Matrix= ', qos)

        for k,v in results.result_ave.items():
            if isinstance(v, list):
                results.result_ave[k] = []
            else:
                results.result_ave[k] = 0.0
            

        q = mp.Queue()
        p_list = [mp.Process(target=comm, args=(const.NODE_MIN,qos,area,q,)) \
            for j in range(NUM_CORE)]
        [p.start() for p in p_list]

        j=0
        while True:
            if q.empty() is False:
                print(' Time = ',j)
                tmp = q.get()
                for k, v in tmp.items():
                    if isinstance(v, str) == True:
                        results.result_ave[k] = v
                    else:
                        results.result_ave[k] += v

                j += 1
                if j == NUM_CORE:
                    break

        [p.join() for p in p_list]
        q.close()

        for k, v in results.result_ave.items():
            if (isinstance(v, str) == False): 
                if isinstance(v, list):
                    results.result_out_system[k] = v
                else:
                    results.result_out[k] = v / float(NUM_CORE)
            else:
                results.result_out[k] = v

        #print('qos =',qos)
        #print('results.result_ave',results.result_ave)

        tmp = pd.DataFrame(results.result_out.values(), \
            index=results.result_out.keys()).T
        df = df.append(tmp, ignore_index = True)
        
        file_name = path + 'qos' + qos[0] + 'results.csv'
        df_system = pd.DataFrame(results.result_out_system.values(), \
            index=results.result_out_system.keys()).T
        df_system.to_csv(file_name)

    file_name = path + 'results.csv'
    df.to_csv(file_name)

if __name__ == "__main__":
    main()  
        
