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
    
    X = np.arange(const.A, const.B, const.DELTA_MESH)
    Y = np.arange(const.A, const.B, const.DELTA_MESH)
    XX, YY = np.meshgrid(X,Y)
    #二次元配列を一次元に
    X = XX.flatten()
    Y = YY.flatten()
    leng = len(X)

    cluNum = np.array([-1 for i in range(leng)])
    counts = np.zeros(leng)
    
    for i in range(leng):
        #範囲にあるdataフレームの抽出
        df_tmp = df[(X[i]<=df['lat']) & (df['lat']<(X[i]+const.DELTA_MESH))\
            & (Y[i]<=df['lon']) & (df['lon']<Y[i]+const.DELTA_MESH)]
        if len(df_tmp) == 0:
            pass
        else :
            clu_variety = df_tmp['cluNum'].value_counts()
            #clusterナンバーの取得
            index_list = clu_variety.index
            if len(index_list) == 1:
                cluNum[i] = index_list[0]
                counts[i] = clu_variety[index_list[0]]
            else :
                #１つのメッシュが複数クラスタに属する場合, それを新規に追加する
                cluNum[i] = index_list[0]
                counts[i] = clu_variety[index_list[0]]
                for j in range(1,len(index_list)):
                    X = np.append(X,X[i])
                    Y = np.append(Y,Y[i])
                    cluNum = np.append(cluNum,index_list[j]) 
                    counts = np.append(counts,clu_variety[index_list[j]])

    leng = len(X)
    trans_prob = np.zeros(leng)
    data = pd.DataFrame({
        'lat':X,
        'lon':Y,
        'cluNum':cluNum,
        'counts':counts,
        'trans_prob':trans_prob
    })
    cluNum_list = list(index_clusterNo_df['ClusterNo'])
    for cluNum in cluNum_list:
        tmp = sum(list(data[data['cluNum']==int(cluNum)]['counts']))
        for index in data[data['cluNum']==int(cluNum)].index:
            data.at[index, 'trans_prob'] = data.at[index, 'counts'] / tmp
    print(data)

    data.to_csv('observationModel.csv')

observeMat(df)