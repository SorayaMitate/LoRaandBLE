import pandas as pd

df = pd.read_csv('test.csv')

df_tmp = df[df.index < 1000]
df_tmp.to_csv('test.csv')