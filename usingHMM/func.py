import random
from math import pi, log10, cos, sqrt
from cmath import exp as cexp
import numpy as np
import pandas as pd
from scipy import optimize
from scipy.special import erfc
import matplotlib.pyplot as plt
import seaborn as sns

def tvtodBm(t):
    a = 10.0*log10(t)
    return a

def dBmtotv(dBm):
    tv = 10.0**(dBm / 10.0)
    return tv

def calc_dist(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def Shadowing():
    return np.random.normal(0.0, 8.0)

def Fading(v, f):
    #到来角一様分布(Jakesモデル)
    #入力 : 移動体の速さ, 中心周波数
    L = 100 #入射パス数
    fc = f #中心周波数 : 920[MHz]
    c = 299792458.0 # 光速[m/sec]
    lam = c / fc
    fd = v / lam #最大ドップラー周波数
    Ts = 128.0

    tmp1 = 0.0
    for i in range(L):
        theta = random.uniform(0.0, 2.0*pi)
        phi = random.uniform(0.0, 2.0*pi)
        tmp1 += cexp(1.0j*(2.0*pi*fd*Ts*i*cos(theta) + phi))
    tmp1 = tmp1 / sqrt(float(L))
    return tvtodBm(abs(tmp1)**2)

def PL(f,dis):
    #減衰定数
    gamma = 3.0
    pii = 4.0*np.pi
    fle = 2.4*10.0**9
    lam = 299792458.0 / f
    if dis == 0:
        loss = -20*np.log10(lam/pii) + gamma*10*np.log10(0.5)
        return loss
    else:
        loss = -20.0*np.log10(lam/pii) + gamma*10*np.log10(dis)
        return loss

def poisson():
    lam = 0.01
    return int(-log10(random.random()) / lam)

#空間相関を持つシャドウィング値を作成する関数
#引数 : メッシュサイズ, メッシュ範囲X, メッシュ範囲Y, 各メッシュの正規分布の分散, 相関距離
#戻り値 : 空間相関をもつシャドウィング
def SpacialColShadowing(size, XSIZE, YSIZE, var, dcol):

    #2地点間の相関係数を計算する関数
    #入力 : 2メッシュ間の距離
    def calc_SpatialCorrelation(d, dcol):
        return np.exp((-1)*d*np.log(2)/dcol)

    X = np.arange(0, XSIZE, size)
    Y = np.arange(0, YSIZE, size)
    XX, YY = np.meshgrid(X,Y)
    #二次元配列を一次元に
    X = XX.flatten()
    Y = YY.flatten()
    leng = len(X)
    S = np.zeros((leng,leng))

    #共分散行列の計算
    for i in range(leng):
        for j in range(leng):
            tmp = calc_dist(X[i],Y[i],X[j],Y[j])
            S[i][j] = calc_SpatialCorrelation(tmp, dcol)*(var**2)
    
    #コレスキー分解
    L = np.linalg.cholesky(S)

    #共分散行列の計算
    w = np.random.standard_normal(leng)
    M = np.dot(L, w)

    mesh = pd.DataFrame({
        'X':X,
        'Y':Y,
        'SHADOWING':M
    })

    return mesh

#LoRa変調でのSNRからBERを算出する関数(AWGNチャネル)
def lora_ber_AWGN(sf, snr):
    snr = pow(10,snr/10.0)
    tmp = np.sqrt(snr*np.power(2,sf+1))-np.sqrt(1.386*sf+1.154)
    return 0.5*0.5*erfc(tmp/np.sqrt(2))

#LoRa変調でのSNRからBERを算出する関数(レイリーフェージング下)
def lora_ber_Raylgh(sf, snr):
    def Hm(m):
        return np.log(m)+1.0/(2.0*m)+0.57722
    snr = np.power(10.0,snr/10.0)
    nakami = 2*Hm(np.power(2,sf)-1)
    sneff = np.power(2,sf)*snr
    kou1 = 0.5*erfc((-1)*np.sqrt(nakami)/np.sqrt(2))
    tmp = (-1)*nakami/(2*(sneff+1))
    kou2 = np.sqrt(sneff/(sneff+1))*np.exp(tmp)
    tmp = np.sqrt((sneff+1)/sneff)*((-1)*np.sqrt(nakami)\
        +np.sqrt(nakami)/(sneff+1))
    kou3 = 0.5*erfc(tmp/np.sqrt(2))
    return 0.5*(kou1-kou2*kou3)
