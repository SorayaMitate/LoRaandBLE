import os
import gc
import math
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from const import *
#from trajectory import *

const = Const()

MAX_LAT = 40.1
MIN_LAT = 39.8
MAX_LON = 116.5
MIN_LON = 116.2

#path_download = 'C:\\Users\\soraya-PC\\Desktop\\Geolife Trajectories 1.3\\Geolife Trajectories 1.3\\Data'
#path_download = '/home/owner/mitate/MieSCOPE/Geolife Trajectories 1.3/Geolife Trajectories 1.3/Data'
path_download = '/home/flab/mitate/data/MieSCOPE/Geolife Trajectories 1.3/Data'
dir_list = glob.glob(path_download + '/*')

trag_path_list = [dir_name + '/Trajectory' for dir_name in dir_list]
file_tmp = []
file_tmp += [glob.glob(dir_name + '/*') for dir_name in trag_path_list]
file_list = [file_name for i in file_tmp for file_name in i]
print('The number of Trajectory =', len(file_list))

data = []

#データタプル
#[(lat, lon, dist)]
tra_num = 1
for file_name in file_list:
    with open(file_name, 'r', newline="") as f:
        #print(file_name)
        tmp = []
        for i in f:
            if len(i.rstrip('\n').split(',')) == 7:
                lat = float(i.rstrip('\n').split(',')[0])
                lon = float(i.rstrip('\n').split(',')[1])
                if MIN_LAT <= lat and lat <= MAX_LAT and MIN_LON <= lon and lon <= MAX_LON:
                    tmp += [(lat, lon, tra_num)]
                else :
                    pass
            else :
                pass
        data += [tmp]
        tra_num += 1
        f.close()

lat = [j[0] for i in data for j in i]
lon = [j[1] for i in data for j in i]
tra_num = [[j[2] for i in data for j in i]]

data = pd.DataFrame({
    'lat':lat,
    'lon':lon,
    'tra_num':tra_num
})

def normarize(data, v_min, v_max):
    norm_num = const.B
    return (data - v_min)/(v_max-v_min) * norm_num

print(data)

data['lat'] = normarize(data['lat'], MIN_LAT, MAX_LAT)
data['lon'] = normarize(data['lon'], MIN_LON, MAX_LON)

print(data)

leng = len(lat)

redata = [[(normarize(j[0], MIN_LAT, MAX_LAT), normarize(j[1], MIN_LON, MAX_LON), j[2])\
    for j in i] for i in data]
print('lenght of redata sets =', len(redata))

lat = [j[0] for i in redata for j in i]
lon = [j[1] for i in redata for j in i]
tra_num = [j[2] for i in redata for j in i]

#メモリ解放
del redata
gc.collect()

#データフレーム定義
df = pd.DataFrame({
    'lat':lat,
    'lon':lon,
    'tra_num':tra_num,
    'segment_num':-1,
    'segment_head':False,
    'cluNum':-1,
    'clu_head':False
})
print(df)

del lat
del lon
del tra_num
gc.collect()

#Alg.1 : Trajectory のクラスタリング
#dataフレーム構成：[緯度, 経度, Trajectory No., cluNum,clu_head']

#reredata = [[j[0], j[1]] for i in redata for j in i]
print('lengh of df =', len(df))
#Trajectory clustring 500m
density_trag_clustering(df, 2000.0, 100)

index_tmp = list(df[df['segment_head'] == True].index)
print(index_tmp)
print('lengh of df(segment_head) =', len(index_tmp))

#Trajectory clustring 100m
tmp_list = [traSeg(df[df['segment_num']==i], 100.0) for i in index_tmp]
i=0
for df_tmp in tmp_list:
    print('lengh of df_tmp =', len(df_tmp))
    if i == 0:
        df = df_tmp
        i += 1
    else:
        df = pd.merge(df, df_tmp, how='outer')
print('lengh of df =', len(df))
#print(df['cluNum'].value_counts())

#メモリ開放
del tmp_list
gc.collect()

df.to_csv('traj_2000.csv')

index_tmp = list(df[df['clu_head'] == True].index)
