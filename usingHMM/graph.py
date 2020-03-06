import random
from math import pi, log10, cos, sqrt
from cmath import exp as cexp
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

#mesh = pd.read_csv('SC_shadowing.csv')
#mesh = mesh[(mesh['X']<=1000)&(mesh['Y']<=1000)]

#pivot = mesh.pivot_table(values=['SHADOWING'], index=['X'], columns=['Y'], dropna= False)
#plt.figure()
#sns.heatmap(pivot,cmap = 'jet', linecolor='Black',square = True)
#plt.show()

df = pd.read_csv('system_results.csv')

sns.set_style("darkgrid")

fig = plt.figure()
ax = Axes3D(fig)

ax.set_xlabel("distance between transmitter and receiver")
ax.set_ylabel("shadowing")
ax.set_zlabel("system")

ax.plot(df['dist'],df['shadowing_avg'],df['clu_system'],marker="o",linestyle='None')
plt.show()