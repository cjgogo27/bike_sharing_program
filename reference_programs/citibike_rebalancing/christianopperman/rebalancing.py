import pandas as pd
import numpy as np
from joblib import load
from predict_bike_dock_demand import predict_bike_dock_demand
from predict_station_status import predict_station_status
import sys

# Define a function that, given a datatime, will generate a dataframe of bike/dock demand and station depletion status
def get_predictions(userDate):
    # Generate separate dataframes from bike/dock demand and station depletion status predictions
    bike_dock_demand = predict_bike_dock_demand(userDate)
    station_satus = predict_station_status(userDate)

    # Merge the two prediction dataframes
    df = pd.merge(bike_dock_demand, station_satus, on = "station_id")
    df = df.drop_duplicates(subset = "station_id").reset_index().drop("index", axis = 1)

    # Map numerical values onto the bike and dock demand for easier indexing
    df.bike_demand = df.bike_demand.map({'High': 3, 'Medium': 2, 'Low': 1})
    df.dock_demand = df.dock_demand.map({'High': 3, 'Medium': 2, 'Low': 1})
    df = df.sort_values('bike_demand', ascending = False)

    return df


# Define a function that, when given a list of stations to bring bikes to, a list of 
# stations to take bikes from, the original dataframe of status and demand predictions,
# and a list (either empty or of paired predictions), generates pairs of stations to/from
# which to rebalance bikes based on closest distance
def generate_pairs(rebalance_in, rebalance_out, original_df, paired_list):
    # Iterate through stations that need bikes added to them
    # Pair each station with the closest station that needs bikes removed
    for i in rebalance_in.station_id:
        out_stations = list(rebalance_out.station_id)
        if len(out_stations) > 0:
            # Find closest station from which to take bikes from
            df = pd.DataFrame(station_dict[i], columns = ['station', 'distance']).set_index('station')
            df = df.loc[out_stations].sort_values('distance')
            nearest_station = int(list(df.index.values)[0])
            
            # Update original dataframe of stations that need rebalancing to reflect the rebalancing
            original_df.loc[original_df['station_id'] == nearest_station, 'depletion_status'] = "Healthy"
            original_df.loc[original_df['station_id'] == i, 'depletion_status'] = "Healthy"
            # Remove the rebalanced station from the data frame of stations to remove bikes from
            rebalance_out = rebalance_out[rebalance_out['station_id']!=nearest_station]
            
            #print(f'Station {i} is closest to Station {nearest_station}')
            paired_list.append((i, nearest_station))
        else:
            break
    return original_df, paired_list


def pair_stations(predictions):
    copy_df = predictions.copy()

    # Initialize empty list to which station pairs will be added
    paired_stations = []

    # Generate a dataframe of stations that need bikes brought in and
    # a dataframe of stations that need bikes taken out
    rebalance_in = copy_df[(copy_df['depletion_status'] == "Empty Risk") & (copy_df['bike_demand']>copy_df['dock_demand'])].reset_index().drop('index', axis = 1)
    rebalance_out = copy_df[(copy_df['depletion_status'] == "Full Risk") & (copy_df['bike_demand']<copy_df['dock_demand'])].reset_index().drop('index', axis = 1)
    
    # Do the initial pass to pair stations
    copy_df, paired_stations = generate_pairs(rebalance_in, rebalance_out, copy_df, paired_stations)
    
    # Check to see if there are still stations that need balancing
    # This will occur if the number of stations that need bikes brought in and the
    # number that need bikes taken out are not equal at the start of the process
    rebalance_in = copy_df[(copy_df['depletion_status'] == "Empty Risk") & (copy_df['bike_demand']>copy_df['dock_demand'])].reset_index().drop('index', axis = 1)
    rebalance_out = copy_df[(copy_df['depletion_status'] == "Full Risk") & (copy_df['bike_demand']<copy_df['dock_demand'])].reset_index().drop('index', axis = 1)

    # If there are still stations that need bikes brought in, take bikes from stations
    # which are full/nearly full and have a medium number of both bikes and slots available
    if rebalance_in.shape[0] > rebalance_out.shape[0]:
        rebalance_out = copy_df[(copy_df.depletion_status == "Full Risk") & np.logical_and(copy_df.bike_demand == 2, copy_df.dock_demand == 2)]
        copy_df, paired_stations = generate_pairs(rebalance_in, rebalance_out, copy_df, paired_stations)
    # If there are still stations that need bikes taken out, take bikes to stations
    # which are empty/nearly empty and have a medium number of both bikes and slots available
    elif rebalance_in.shape[0] < rebalance_out.shape[0]:
        rebalance_in = copy_df[(copy_df.depletion_status == "Empty Risk") & np.logical_and(copy_df.bike_demand == 2, copy_df.dock_demand == 2)]
        copy_df, paired_stations = generate_pairs(rebalance_in, rebalance_out, copy_df, paired_stations)
    
    return(pd.DataFrame(paired_stations, columns = ["Rebalance Bikes To Station #", "Rebalance Bikes From Station #"]), copy_df)


########################################### MAIN ###########################################
userDate=sys.argv[1]
try:
    temp=pd.to_datetime(userDate)
    print (f"Datetime provided: {userDate}")
except ValueError:
    print("Oops!  That was not a datetime.  Try again...")

# Generate predictions bike_demand, dock_demand, station_status
df=get_predictions(userDate)

station_dict = load('../Data/station_dict.pkl')
# Generate a rebalancing strategy: 
pair_list, _ = pair_stations(df)

# Save rebalancing strategies to CSV files
pair_list.to_csv('../Results/matched_rebalancing_stations_{userDate}.csv', index = False)


