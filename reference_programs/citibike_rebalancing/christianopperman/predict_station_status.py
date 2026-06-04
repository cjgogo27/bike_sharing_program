import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
from joblib import dump, load
import sys

#### Define a function that takes a date and time and generates a dataframe of each CitiBike station's depletion status
def predict_station_status(user_datetime):
    # Import list of currently active stations. Random Forest machine learning model, and Label Encoder
    le = load('../Models/seasonencoder.joblib')
    rf = load('../Models/depletion_status_classifier.joblib')
    live_stations = pd.read_csv('../Data/live_stations.csv')

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

    # Create a dataframe containing all currently live docks and the provided datetime.
    # The dataframe will be fed to the random forest model to generate depletion status predictions
    stations = pd.DataFrame(columns = ['dock_id', 'hour', 'minute', 'dayofweek', 'season'])
    # Create a row for each live dock
    stations['dock_id'] = live_stations['station_id']
    # Initialize the hour, minute, dayofweek, and season for each row
    stations.loc[:, 'hour'] = user_df['hour'][0]
    stations.loc[:, 'minute'] = user_df['minute'][0]
    stations.loc[:, 'dayofweek'] = user_df['dayofweek'][0]
    stations.loc[:, 'season'] = user_df['season'][0]
    
    # Generate depletion status predictions
    status=rf.predict(stations)

    # Create and return a dataframe with each live station and the depletion status predictions
    station_status = pd.DataFrame(
        {'station_id': live_stations['station_id'],
         'depletion_status': pd.Series(status)})
    
    return station_status



