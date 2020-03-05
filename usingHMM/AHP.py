#Proposed Method

import numpy as np
from sympy import * 

#自作モジュール
import Node
import const 
import Result
from func import *
from LoRa import *
from BLE import *

const = Const()

def ahp_normrize(value_dict):
    min_value = min(value_dict.values())
    value_dict_norm = {}
    for k, v in value_dict.items():
        value_dict_norm[k] = min_value / v
    return value_dict_norm

def AdaptionAlgorithm_AHP(system_list, qos_matrix, value1, value2,value3):
    #動的に拡散率を選択するアルゴリズム
    #N各拡散率のNODE数から一番許容量と少ない拡散率へ割り当て
    #入力：許容可能な拡散率セット、各拡散率のノード数
    #出力：ノードの拡散率

    # 比較行列から重みベクトルを計算する関数
    def calc_ahp_weight_vec(comparison_mat):
        
        # 固有値のインデックス
        EIGEN_VAL_IDX = 0    
        # sympyの関数を使って、固有値と固有ベクトルを得る
        eigen_val_vects = comparison_mat.eigenvects()
        # 最大固有値とその時の多重度・固有ベクトルを取得
        eigen_val, multiplicity, eigen_vec = max(eigen_val_vects, key=(lambda x: x[EIGEN_VAL_IDX]))
        # 重みの合計が1になるように標準化
        weight_vec = eigen_vec[0] / sum(eigen_vec[0])
        
        # 重みを返す
        return(weight_vec)

    ahp_Matrix = Matrix([])

    for sf in system_list:
        ahp_Matrix = ahp_Matrix.row_insert(len(system_list), \
            Matrix([[value1[sf], value2[sf],value3[sf]]]))

    eval_mat_1 = calc_ahp_weight_vec(qos_matrix)
    tmp_mat = ahp_Matrix * eval_mat_1
    tmp_mat = tmp_mat[:]

    #----------デバック----------#
    #print('qos_matrix =', qos_matrix)
    #print('eval_mat =',eval_mat_1)
    #print('ahp_matrix =',ahp_Matrix)
    #print('tmp_mat =', tmp_mat)
    #print('SF=', system_list[tmp_mat.index(max(tmp_mat))])

    return system_list[tmp_mat.index(max(tmp_mat))]
