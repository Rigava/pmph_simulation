import pandas as pd
from pathlib import Path
import scipy.interpolate
import math

seg_df = pd.read_excel("GM.xlsx", engine="openpyxl")
print(seg_df.head())
df_unpivot=seg_df.melt(id_vars='Speed',var_name='SegmentSize',value_name='TotalFuel')
df_unpivot = df_unpivot.dropna()
df_unpivot.to_csv('GM_output.csv')
