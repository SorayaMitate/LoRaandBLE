import random
from math import pi, log10, cos, sqrt
from cmath import exp as cexp
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt
import seaborn as sns

mesh = pd.read_csv('SC_shadowing.csv')

pivot = mesh.pivot_table(values=['SHADOWING'], index=['X'], columns=['Y'], dropna= False)
plt.figure()
sns.heatmap(pivot,cmap = 'jet',linewidths=0.5, linecolor='Black',square = True)
plt.savefig('map.png')
