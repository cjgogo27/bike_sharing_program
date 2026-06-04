import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def mip_routing_result():
    station_num=57
    df = pd.read_csv("data/service_level_result.csv")
    df.drop(df[(df["smin"]==0)&(df["smax"]==0)].index,inplace=True)
    df.reset_index(inplace=True,drop=True)
    station = pd.read_csv("data/station_info.csv")
    st_list = list(df["id"].astype(int))
    print(list(df["id"].astype(int)))
    station = station[station["id"].isin(st_list)]
    station.reset_index(inplace=True,drop=True)
    
    print(station)
    # unservice = df.loc[(df["smin"]>df["start"])|(df["smax"]<df["start"])]
    station_condition = pd.read_csv("data/station_condition.csv").tail(station_num)
    station_condition.reset_index(inplace=True,drop=True)
    df["after3"] = station_condition["bike"]
    
    result = np.load("data/np_save.npy")   

    check = result[0][0][0][0]
    check2 = result[1][0][0][0]
    #np shape(vehicle num, time interval, drop & pickup, arc)
    for i in range(len(result[0])):
        if result[0][i][0][0]!=0 and result[0][i][0][1]!=0:
            check = np.concatenate((check,result[0][i][0][1]),axis=None)
        if result[1][i][0][0]!=0 and result[1][i][0][1]!=0:
            check2 = np.concatenate((check2,result[1][i][0][1]),axis=None)
    print(check)
    print(check2)
    vehicle1_visit_station = station.loc[check]
    vehicle1_visit_station.drop_duplicates(inplace = True)
    
    vehicle2_visit_station = station.loc[check2]
    vehicle2_visit_station.drop_duplicates(inplace = True)

    plt.scatter(x=vehicle1_visit_station['lng'], y=vehicle1_visit_station['lat'])
    plt.scatter(x=vehicle2_visit_station['lng'], y=vehicle2_visit_station['lat'])

    plt.show()
    df.drop(columns=["Unnamed: 0"],inplace=True)
    
    
    routing_plan = np.empty(0)
    for i in range(len(check)):
        routing_plan = np.concatenate((routing_plan,df.iloc[int(check[i])]["id"]),axis=None)
        
    print(routing_plan)

if __name__ =='__main__':
    mip_routing_result()