import re
import random
from math import pi, log10, cos, sqrt
from cmath import exp as cexp
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib
import matplotlib.pyplot as plt
import glob
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

from const import *

#mesh = pd.read_csv('SC_shadowing.csv')
#mesh = mesh[(mesh['X']<=1000)&(mesh['Y']<=1000)]

#pivot = mesh.pivot_table(values=['SHADOWING'], index=['X'], columns=['Y'], dropna= False)
#plt.figure()
#sns.heatmap(pivot,cmap = 'jet', linecolor='Black',square = True)
#plt.show()

path = 'C:\\Users\\soraya-PC\\code\\results\\system\\shaped\\'
file_list = glob.glob(path+'*')

sns.set_style("darkgrid")

#fig = plt.figure()
#ax = Axes3D(fig)

#ax.set_xlabel("distance between transmitter and receiver")
#ax.set_ylabel("shadowing")
#ax.set_zlabel("system")

const = Const()

BIN = 200
dist_bin = np.arange(BIN, 1400, BIN)

'''
fig, ax = plt.subplots(figsize=(10, 8))
for_replace = r'C:\\Users\\soraya-PC\\code\\results\\system\\'
for f in file_list:
    df = pd.read_csv(f)
    
    #結果格納用
    result = {'dist':[],const.SF7:[],const.SF8:[],const.SF10:[]\
        ,const.SF11:[],const.SF12:[],const.BLE:[]} 

    for d in dist_bin:
        result['dist'].append(d)
        tmp = df[(d-BIN<=df['dist'])&(df['dist']<d)]
        
        for system in const.SYSTEM_LIST:
            result[system].append(len(tmp[tmp['clu_system']==system]) / len(tmp))
    
    #ファイル名の置換
    file_name = f.replace(path,'re')
    tmp = pd.DataFrame(result.values(), index=result.keys()).T
    tmp.to_csv(path+file_name)
    tmp.T.plot(kind='bar', stacked=True, ax=ax)
plt.legend()
plt.show()
'''
plt.style.use('ggplot') 
font = {'family' : 'meiryo'}
matplotlib.rc('font', **font)
plt.legend

for f in file_list:
    df = pd.read_csv(f,index_col='dist')
    df = df.drop('Unnamed: 0', axis=1)
    file_name = f.replace(path,'')
    file_name = file_name.replace('.csv','.png')
    df.plot.bar(stacked=True,label=file_name)
    plt.savefig(file_name)

#ax.plot(df['dist'],df['shadowing_avg'],df['clu_system'],marker="o",linestyle='None'\
#    ,label=f)
#plt.scatter(df['dist'],df['clu_system'],label=f)
#plt.show()