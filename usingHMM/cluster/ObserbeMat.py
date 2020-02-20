#観測モデルの作成

import pandas as pd

from 

# lat, lon, tra_num, segment_num, segment_head, cluNum, clu_head
df = pd.read_csv('data/traj_2000.csv', index_col=0)


# 入力 : dataフレーム, map[x, y, dist, shadowing]
# 出力 : 観測モデル
def observeMat(df, map):
    map     
