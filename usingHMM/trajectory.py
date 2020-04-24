from math import sqrt
import csv
import gc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools

import const

conts = const.Const()

def calc_dist(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

#ネイバーのインデックスを返す変数
def getNeighbors(data, point, r):
    data['dist'] = calc_dist(data['lat'],data['lon'],point['lat'],point['lon'])
    neighbors = data[data['dist']<=r].index
    return neighbors

#軌道のクラスタリング
#入力：datasets['lat', 'lon', 'tra_num', 'Segment_num', 'segment_head', 'cluNum', 'clu_head']
#出力：①datasets['segment']に対応するナンバーを代入
#　　　②clusterheadの番号
def density_trag_clustering(data, r, minpts):
    length = len(data)
    data['flag'] = -1
    for i in range(length):
        if data.at[i, 'flag'] == -1 :
            S = getNeighbors(data, data.loc[i], r)

            print('len(neighbors) = ',len(S))
            
            if len(S) < minpts:
                pass
            else:
                #Flag処理
                data.at[i, 'flag'] = 1
                #data.at[i,'segment_head'] = True
                data.at[i,'clu_head'] = True
                for j in S:
                    data.at[j, 'flag'] = 1
                    #data.at[j,'segment_num'] = i
                    data.at[j,'cluNum'] = i
        else :
            pass
        
        print('len(data[data[cluNum]==%d])'%i,len(data[data['cluNum']==i]))
    
    data.drop('dist', axis=1)
    data.drop('flag', axis=1)

#######ここいる？？？？？？？？？
#各セグメント→クラスタリングによるhidden nodeの抽出
#入力：datasets['lat', 'lon', 'tra_num', 'Segment_num(指定)', 'segment_head', 'cluNum', 'clu_head'],  距離
#出力：①datasets['cluNum']に対応するナンバーを代入
#　　　②clusterheadの番号
def traSeg(datasets, r):
    index = list(datasets.index)
    for i in index:
        if datasets.at[i, 'cluNum'] != -1:
            #Flag処理
            pass
        else :
            datasets.at[i, 'cluNum'] = i
            datasets.at[i, 'clu_head'] = True
            for j in index:
                if datasets.at[j, 'cluNum'] != -1:
                    pass
                else :
                    if calc_dist(datasets.at[i,'lat'], datasets.at[i,'lon'], datasets.at[j,'lat'], datasets.at[j,'lon']) < r:
                        datasets.at[j, 'cluNum'] = i
                    else :
                        pass
    return datasets

#trajctoryと遷移確率の出力
#出力：遷移確率, クラスタNo.とインデックスの対応(辞書), (二次元リスト)軌跡の一覧, (リスト)cluster名
def trajectory(df):

    #Groupbyによるデータフレーム分割(Segment毎)
    #df_dict = {}
    #for name, group in df.groupby('segment_num'):
    #    df_dict[name] = group

    #初期化
    cluNum_2dlist = []

    #cluster_noの抽出   
    cluster_no_list = df['cluNum'].unique()
    #trajectoryでグループ化
    for name, group in df.groupby('tra_num'):
        cluNum_list = []
        tmp = -1
        for cluNum in group['cluNum']:
            if tmp != cluNum:
                cluNum_list.append(cluNum)
                tmp = cluNum
            else:
                pass
        if len(cluNum_list) > 1:
            cluNum_2dlist.append(cluNum_list)
        else :
            pass

    #クラスタの遷移確率の算出
    def trans_prob(d2seniretu, columns):

        length_columns = len(columns)
        #0～Nの対応辞書の作成
        index_dict = {}
        j=0
        for i in columns:
            index_dict[i] = j
            j += 1
        prob_matrix = np.zeros((length_columns,length_columns))

        for seniretu in d2seniretu:
            length_seniretu = len(seniretu)

            for i in range(length_seniretu-1):
                tmp = i+1
                for x, y in itertools.product(columns, columns):
                    if seniretu[i] == x and seniretu[tmp] == y:
                        prob_matrix[index_dict[x]][index_dict[y]] += 1
                    else :
                        pass

        row_sum = np.sum(prob_matrix, axis=1).reshape([length_columns,1])
        row_sum = np.where(row_sum<=0, 1, row_sum)
        prob_matrix = prob_matrix / row_sum

        return prob_matrix, index_dict

    trans_prob_mat, trans_prob_mat_index = trans_prob(cluNum_2dlist, cluster_no_list)

    #遷移確率のcsv保存
    np.savetxt('TransProb_matrix.txt', trans_prob_mat)

    print('trans_prob_mat_index =',trans_prob_mat_index)
    #print('cluster_no_list =', cluster_no_list)
    #print('trans_prob.shape =', trans_prob_mat.shape)

    #辞書⇒データフレーム
    ###########いらない気がするなあ
    #key_list = [i for i in trans_prob_mat_index.values()]
    #value_list = [i for i in trans_prob_mat_index.keys()]
    #index_df = pd.DataFrame({
    #    'indexName':key_list,
    #    'ClusterNo':value_list
    #})
    #index_df.to_csv('data/IndextoClusterNo_df.csv')

    #Trajectoryリストの保存
    ##########いらない気がするなあ
    #with open('data/Trajectory_list.csv', 'w', newline='') as f:
    #    writer = csv.writer(f, delimiter=",")
    #    [writer.writerow(i) for i in cluNum_2dlist]

def CluNumtoPosi(cluNum, df):
    x = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lat']
    y = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lon']
    return float(x),float(y)

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
    cluNum_list = df['cluNum'].unique()
    for cluNum in cluNum_list:
        tmp = sum(list(data[data['cluNum']==int(cluNum)]['counts']))
        for index in data[data['cluNum']==int(cluNum)].index:
            data.at[index, 'trans_prob'] = data.at[index, 'counts'] / tmp
    print(data)

    data.to_csv('observationModel.csv')