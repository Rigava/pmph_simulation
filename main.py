import pandas as pd
import numpy as np
from pathlib import Path
import scipy.interpolate
import math
import matplotlib.pyplot as plt

seg_df = pd.read_csv("GM_output.csv")

def get_ft(segmentSize):
    filter_seg = (seg_df['SegmentSize']==segmentSize) 
    # & (seg_df['Draft']==10)
    df = seg_df[filter_seg]
    return df
def get_sim_cons(segmentSize, speed, new_speed):
    # Getting the fuel table rows for the imo
    table = get_ft(segmentSize)
    tot_fuel = scipy.interpolate.interp1d(table.Speed.values,table.TotalFuel.values)
    # Returning the interpolated values for actual and simulation
    return (
        new_speed, 
        tot_fuel(speed).round(3),
        tot_fuel(new_speed).round(3)
    )
def add_new_columns(temp_table):

    temp_table['new_seaspeed'],\
        temp_table['tot_fuel_actual'],\
            temp_table['tot_fuel_sim']  = np.vectorize(get_sim_cons)(temp_table['segmentSize'],
                                                                     temp_table['SeaSpeed'], 
                                                                     temp_table['new_speed'],
                                                                    )
    return temp_table

# LOAD THE MAIN DATA
df=pd.read_csv("data.csv")
print(df.dtypes)
# print(df.head(5))
df['avg_reduction']=1
df['tot_reduction']=df['avg_reduction']*df['all legs']
df['new_sea_running_hrs']=df['seaMEHours']+df['tot_reduction']
df['new_speed']=df['Total SeaDistance']/df['new_sea_running_hrs']
print(df)
df_ps = add_new_columns(df[:1])
df_ps['newSE_hr']=df_ps['seaEmission per hr']*df_ps['tot_fuel_sim']/df_ps['tot_fuel_actual']
df_ps['newSE']=df_ps['newSE_hr']*df_ps['new_sea_running_hrs']
df_ps['emission_red']=df_ps['sea cons emission']-df_ps['newSE']
df_ps['residual_fuel_saving'] = df_ps['emission_red']/3.114
df_ps['fuelSave_reduction'] = df_ps['residual_fuel_saving'] / df['tot_reduction']
print(df_ps.head())
plt.barh(df_ps['segmentSize'],df_ps['fuelSave_reduction'])
plt.xlabel("Segments")
plt.show()
# df_ps.to_csv('main_output.csv')
