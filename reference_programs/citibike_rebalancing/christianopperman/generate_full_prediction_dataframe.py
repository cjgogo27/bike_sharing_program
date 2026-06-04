import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
from joblib import dump, load


##### Import necessary data and machine learning models
# Import Random Forest machine learning model and Label Encoder
le = load('../Models/seasonencoder.joblib')
rf = load('../Models/depletion_status_classifier.joblib')

# Import list of currently active stations
live_stations = pd.read_csv('../Data/live_stations.csv')
# Import bike/slot demand predictions for chosen target datetime (7-15-2020 9:00)
demand_07152020 = pd.read_csv('../Data/bike_demand_prediction2020-07-15 9_00.csv')
demand_09102020 = pd.read_csv('../Data/bike_demand_prediction2020-09-10 17_00.csv')
demand_11042020 = pd.read_csv('../Data/bike_demand_prediction2020-11-04 13_00.csv')


#### Define function to take a date and time and convert it into a dataframe input for prediction
def process_input(user_datetime):
    # Check to see if the provided date is in the correct format
    try:
        user_datetime = datetime.strptime(user_datetime, '%m-%d-%Y %H:%M')
        print(f"The provided datetime is: {user_datetime}")
    except:
        print("The provided datetime was in an incorrect format")
    
    # Create a dataframe for prediction input
    # Dataframe should be in the format of hour | minute | dayofweek | season
    # 'dayofweek' is numeric (0-6) starting on Monday
    user_df = pd.DataFrame([[user_datetime.hour, user_datetime.minute, user_datetime.weekday(), user_datetime.month]], columns = ["hour", "minute", "dayofweek", "season"])
    
    # The season column is numeric, corresponding to {0: 'fall', 1: 'spring', 2: 'summer', 3: 'winter'}.
    # Convert month to season and then encode it
    user_df['season'] = user_df['season'].apply(lambda x: 'winter' if x <=2 else 'spring' if x<=5 else 
                                              'summer' if x<=8 else 'fall' if x<=11 else 'winter')
    user_df['season'] = le.transform(user_df['season'])
    return user_df


#### Define function to generate a dataframe combining all sation docks and the user-provided datetime information
def generate_docks(user_datetime_df):
    stations = pd.DataFrame(columns = ['dock_id', 'hour', 'minute', 'dayofweek', 'season'])
    # Create a row for each live dock
    stations['dock_id'] = live_stations['station_id']
    # Initialize the hour, minute, dayofweek, and season for each row
    stations.loc[:, 'hour'] = user_datetime_df['hour'][0]
    stations.loc[:, 'minute'] = user_datetime_df['minute'][0]
    stations.loc[:, 'dayofweek'] = user_datetime_df['dayofweek'][0]
    stations.loc[:, 'season'] = user_datetime_df['season'][0]
    
    return stations


#### Define a function to predict station status
def predict_status(df):
    return rf.predict(df)


#### Define a function that takes all the above steps and performs them at once
def station_status_pipeline(user_datetime):
    user_input = process_input(user_datetime)
    status = predict_status(generate_docks(user_input))
    final_prediction = pd.DataFrame(
        {'station_id': live_stations['station_id'],
         'depletion_status': pd.Series(status)})
    final_prediction = pd.concat([final_prediction, live_stations[['station_lat', 'station_long']]], axis = 1)
    return final_prediction


#### Define a function that takes the full prediction pipeline and merges it with the imported bike/slot demand dataframe
def all_station_demand(user_datetime, df):
    depletion_df = station_status_pipeline(user_datetime)
    final_df = df.merge(depletion_df, on = "station_id")
    final_df = final_df.drop_duplicates(subset = "station_id").reset_index().drop("index", axis = 1)
    return final_df

#### Generate and save the final dataframe with bike/slot demand and station status for chosen target datetimes
# Times: 7-15-2020 9:00; 09-10-2020 17:00, 11-04-2020 13:00
prediction_07152020 = all_station_demand('7-15-2020 9:00', demand_07152020)
prediction_09102020 = all_station_demand('7-15-2020 9:00', demand_09102020)
prediction_11042020 = all_station_demand('7-15-2020 9:00', demand_11042020)

# Save final dataframes to a .csv file for later use
prediction_07152020.to_csv('../Data/station_predictions_07152020.csv', index = False)
prediction_09102020.to_csv('../Data/station_predictions_09102020.csv', index = False)
prediction_11042020.to_csv('../Data/station_predictions_11042020.csv', index = False)

