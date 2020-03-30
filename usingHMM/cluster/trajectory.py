from math import sqrt
import csv
import gc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools

def calc_dist(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

#ネイバーのインデックスを返す変数
def getNeighbors(data, point, r):
    data['dist'] = calc_dist(data['lat'],data['lon'],point['lat'],point['lon'])
    neighbors = data[(data['dist']<=r)&(data['flag']==-1)].index
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
            #Flag処理
            data.at[i, 'flag'] = 1
            S = getNeighbors(data, data.loc[i], r)
            if len(S) < minpts:
                pass
            else:
                data.at[i,'segment_head'] = True
                for j in S:
                    data.at[i, 'flag'] = 1
                    data.at[j,'segment_num'] = i
        else :
            pass
    
    data.drop('dist', axis=1)
    data.drop('flag', axis=1)

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

#システムモデルの生成
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

    row_sum = np.sum(prob_matrix, axis=1).reshape([length_columns,1])
    row_sum = np.where(row_sum<=0, 1, row_sum)
    prob_matrix = prob_matrix / row_sum

    return prob_matrix, index_dict

#観測モデルの生成
def observe_prob():
    pass

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

    trans_prob_mat, trans_prob_mat_index = trans_prob(cluNum_2dlist, cluster_no_list)

    print('trans_prob_mat_index =',trans_prob_mat_index)
    print('cluster_no_list =', cluster_no_list)
    print('trans_prob.shape =', trans_prob_mat.shape)

    #辞書⇒データフレーム
    key_list = [i for i in trans_prob_mat_index.values()]
    value_list = [i for i in trans_prob_mat_index.keys()]
    index_df = pd.DataFrame({
        'indexName':key_list,
        'ClusterNo':value_list
    })
    index_df.to_csv('data/IndextoClusterNo_df.csv')

    #遷移確率のcsv保存
    np.savetxt('data/TransProb_matrix.txt', trans_prob_mat)

    #Trajectoryリストの保存
    with open('data/Trajectory_list.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=",")
        [writer.writerow(i) for i in cluNum_2dlist]

    return trans_prob_mat, trans_prob_mat_index, cluNum_2dlist, cluster_no_list

def CluNumtoPosi(cluNum, df):
    x = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lat']
    y = df[(df['cluNum']==cluNum) & (df['clu_head']==True)]['lon']
    return float(x),float(y)