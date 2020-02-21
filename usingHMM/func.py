import random
from math import pi, log10, cos, sqrt
from cmath import exp as cexp
import numpy as np

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

def per_gaussian(avg):
    tmp = np.random.normal(avg, 0.01)
    if tmp < 0.0:
        tmp = 0.0
    return tmp

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
    gamma = 2.5
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
