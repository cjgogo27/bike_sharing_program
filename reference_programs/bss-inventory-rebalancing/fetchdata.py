import pandas as pd

def fetchdata(start_date,end_date,start_time,end_time,area):
    
    #raw triprecord from 4/1 to 4/10
    df = pd.read_csv("data/triprecord.csv")
    df.drop(columns=["Unnamed: 0"],inplace=True)
    station_info = pd.read_csv("data/station_info.csv")
    station_info.drop(columns=["Unnamed: 0"],inplace=True)
    station_info = station_info.loc[station_info['area'].isin(area)]
    station_info.reset_index(inplace=True,drop=True)

    station_condition = pd.read_csv("data/station_condition.csv")
    # station_condition.columns=["id","recordid","bike","recordtime","free","active","last"]
    # new_row = pd.DataFrame({'id':501209098, 'recordid':111, 'bike':7, 'recordtime':'2023-04-01 06:00:25','free':8,'active':1,'last':00}, index=[0])
    # station_condition = pd.concat([new_row,station_condition.loc[:]]).reset_index(drop=True)
    # 
    

    target_station_id = list(station_info["id"])
    station_condition = station_condition.loc[station_condition['id'].isin(target_station_id)]
    station_condition["capacity"]=station_condition["bike"]+station_condition["free"]


    df["rent_time"]=pd.to_datetime(df["rent_time"])
    df["time"]=pd.to_datetime(df["time"])

    start_df = df.loc[((df["rent_time"].dt.day<=end_date) & (df["rent_time"].dt.day>=start_date)) & \
                ((df["rent_time"].dt.time>=start_time) & (df["rent_time"].dt.time<=end_time))]
    
    end_df = df.loc[((df["time"].dt.day<=end_date) & (df["time"].dt.day>=start_date)) & \
                ((df["time"].dt.time>=start_time) & (df["time"].dt.time<=end_time))]

    start_df = start_df.loc[start_df['rent_s_no'].isin(target_station_id)]
    end_df=end_df.loc[end_df['s_no'].isin(target_station_id)]
    end_df.to_csv("data/end_triprecord.csv")
    start_df.to_csv("data/start_triprecord.csv")
    return station_condition['id'].nunique()
