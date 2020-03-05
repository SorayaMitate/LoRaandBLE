import random
from math import pi, log10, cos, sqrt
from cmath import exp as cexp
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt
import seaborn as sns

mesh = pd.read_csv('SC_shadowing.csv')

mesh = mesh[(mesh['X']<=1000)&(mesh['Y']<=1000)]

pivot = mesh.pivot_table(values=['SHADOWING'], index=['X'], columns=['Y'], dropna= False)
plt.figure()
sns.heatmap(pivot,cmap = 'jet', linecolor='Black',square = True)
plt.show()
