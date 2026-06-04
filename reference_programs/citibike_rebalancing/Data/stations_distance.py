import pandas as pd
import numpy as np
import pickle

stations = pd.read_csv('../Data/live_stations.csv') # all stations after '2019-12-01'

station_dict={}
for station in stations.station_id.unique().tolist():
    loc1=(stations[stations.station_id==station].station_lat.values,stations[stations.station_id==station].station_long.values)
    others=[x for x in stations.station_id.unique().tolist() if x != station]
    dist_to_others={}
    for othr_station in others:
        loc2=(stations[stations.station_id==othr_station].station_lat.values,stations[stations.station_id==othr_station].station_long.values)
        distance=(abs(loc1[0]-loc2[0])+abs(loc1[1]-loc2[1]))[0]
        dist_to_others[othr_station]=distance
    dist_to_others=sorted(dist_to_others.items(), key = lambda kv:(kv[1], kv[0])) # sort by smallest distance
    station_dict[station]=dist_to_others


output = open('station_dict.pkl', 'wb')
pickle.dump(station_dict, output, -1)
output.close()