import os
import gc
import math
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from const import *
from trajectory import *

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

lat_list = []
lon_list = []
tra_num_list = []
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
                    lat_list.append(lat)
                    lon_list.append(lon)
                    tra_num_list.append(tra_num)
                else :
                    pass
            else :
                pass
        tra_num += 1
        f.close()

data = pd.DataFrame({
    'lat':lat_list,
    'lon':lon_list,
    'tra_num':tra_num_list,
    'segment_num':-1,
    'segment_head':False,
    'cluNum':-1,
    'clu_head':False
})

def normarize(data, v_min, v_max):
    norm_num = const.B
    return (data - v_min)/(v_max-v_min) * norm_num

data['lat'] = normarize(data['lat'], MIN_LAT, MAX_LAT)
data['lon'] = normarize(data['lon'], MIN_LON, MAX_LON)

print('lenght of rata sets =', len(data))

del lat
del lon
del tra_num
gc.collect()

#Alg.1 : Trajectory のクラスタリング
#dataフレーム構成：[緯度, 経度, Trajectory No., cluNum,clu_head']
#reredata = [[j[0], j[1]] for i in redata for j in i]
#Trajectory clustring
density_trag_clustering(data, const.CLUSTER_SIZE, 100)
print(data)
data.to_csv('trajectory.csv')

index_tmp = list(data[data['segment_head'] == True].index)

#Trajectory clustring 100m
tmp_list = [traSeg(data[data['segment_num']==i], const.CLUSTER_SIZE) for i in index_tmp]
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
