import pandas as pd
import numpy as np
from pathlib import Path
import scipy.interpolate
import streamlit as st

def load_data():
    upload1 = st.file_uploader("Load your data")
    df=pd.read_csv(upload1)
    upload2 = st.file_uploader("Choose the segment fuel table data")
    seg_df =pd.read_csv(upload2)
    return df,seg_df
df,seg_df = load_data()

def get_ft(segmentSize):
    filter_seg = (seg_df['SegmentSize']==segmentSize) 
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

def main():
    st.title("PMPH Impact by JOSH@I")
    st.subheader("Without data you are just another person with opinion")
    # df,seg_df = load_data()
    
    if st.button("Submit"):
        with st.spinner("processing"):
            df['avg_reduction']=1
            df['tot_reduction']=df['avg_reduction']*df['all legs']
            df['new_sea_running_hrs']=df['seaMEHours']+df['tot_reduction']
            df['new_speed']=df['Total SeaDistance']/df['new_sea_running_hrs']
            df_ps = add_new_columns(df)
            df_ps['newSE_hr']=df_ps['seaEmission per hr']*df_ps['tot_fuel_sim']/df_ps['tot_fuel_actual']
            df_ps['newSE']=df_ps['newSE_hr']*df_ps['new_sea_running_hrs']
            df_ps['emission_red']=df_ps['sea cons emission']-df_ps['newSE']
            df_ps['residual_fuel_saving'] = df_ps['emission_red']/3.114
            df_ps['fuelSave_reduction'] = df_ps['residual_fuel_saving'] / df['tot_reduction']
            print(df_ps.head())
            fil= df_ps['Year']==2023
            chart_data = df_ps[["segmentSize","fuelSave_reduction"]][fil]
            st.bar_chart(chart_data,x='segmentSize',y='fuelSave_reduction')


if __name__ == "__main__":
    main()