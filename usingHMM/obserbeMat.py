#観測モデルの作成

import numpy as np
import pandas as pd

from const import *
from func import *

const = Const()

path = '/home/owner/mitate/MieSCOPE/data/usingHMM/'
df = pd.read_csv(path + 'data/traj_2000.csv', index_col=0)
#df = pd.read_csv('test.csv', index_col=0)
index_clusterNo_df = pd.read_csv(path + 'data/IndextoClusterNo_df.csv', index_col=0, \
    usecols=['indexName','ClusterNo'])

# 入力 : dataフレーム
# 出力 : 観測モデル
def observeMat(df):
    
    dict_tmp = {}
    
    map = [(i, j) for i in range(const.A,const.B+const.DELTA_MESH, const.DELTA_MESH) \
            for j in range(const.A, const.B+const.DELTA_MESH, const.DELTA_MESH)]
    
    leng = len(map)
    for i in range(leng):
        #範囲にあるdataフレームの抽出
        df_tmp = df[(map[i][0]<=df['lat']) & (df['lat']<(map[i][0]+const.DELTA_MESH))\
            & (map[i][1]<=df['lon']) & (df['lon']<map[i][1]+const.DELTA_MESH)]
        if len(df_tmp) == 0:
            map[i] += (-1, 0, 0.0)
        else :
            clu_variety = df_tmp['cluNum'].value_counts()
            #clusterナンバーの取得
            index_list = clu_variety.index
            if len(index_list) == 1:
                map[i] += (index_list[0], clu_variety[index_list[0]], 0.0)
            else :
                #１つのメッシュが複数クラスタに属する場合, それを新規に追加する
                tmp = [map[i] for j in range(len(index_list))]
                map[i] += (index_list[0], clu_variety[index_list[0]], 0.0)
                for j in range(1,len(index_list)):
                    tmp[j] += (index_list[j], clu_variety[index_list[j]], 0.0)
                    map.append(tmp[j])

    data = pd.DataFrame(map)
    data = data.rename(columns={0:'lat', 1:'lon', 2:'cluNum', 3:'counts', 4:'trans_prob'})
    cluNum_list = list(index_clusterNo_df['ClusterNo'])
    for cluNum in cluNum_list:
        tmp = sum(list(data[data['cluNum']==int(cluNum)]['counts']))
        for index in data[data['cluNum']==int(cluNum)].index:
            data.at[index, 'trans_prob'] = data.at[index, 'counts'] / tmp
    print(data)

    data.to_csv('observationModel.csv')

observeMat(df)