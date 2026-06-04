import pandas as pd
import numpy as np
from kol import kolmogorov_forward_equation

def service_level(station_num):
    station_info = pd.read_csv('data/station_condition.csv')
    station_info['capacity'] = station_info['bike']+station_info['free']
    cap=list(station_info['capacity'][:station_num ])
    start = list(station_info['bike'][:station_num ])
    station_list = list(station_info['id'].unique())
    result = np.zeros((station_num,5))
    trip_start = pd.read_csv("data/start_triprecord.csv")
    trip_end = pd.read_csv("data/end_triprecord.csv")
    for i in range(station_num):
        station = station_list[i]
        current_trip_start = trip_start[trip_start["rent_s_no"]==station]

        current_trip_end = trip_end[trip_end["s_no"]==station]
        mu = len(current_trip_start)/180
        lam = len(current_trip_end)/180


        result[i][0],result[i][1] = kolmogorov_forward_equation(mu,lam,cap[i])
        result[i][2] = station
        result[i][3] = cap[i]
        result[i][4] = start[i]


    df = pd.DataFrame(result, columns = ['smin','smax','id','capacity','start'])
    df.to_csv('data/service_level_result.csv')





    
    


