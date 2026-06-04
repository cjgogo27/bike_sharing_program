import sys
import pandas as pd
import numpy as np
import time
from joblib import dump, load
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

def predict_bike_dock_demand(datetime_):
    try:
        temp=pd.to_datetime(datetime_)
        print(f"The provided datetime is: {datetime_}")
    except ValueError:
        print("The provided datetime was in an incorrect format")

    stations = pd.read_csv('../Data/live_stations.csv')[['station_id']]
    stations=stations.drop_duplicates().reset_index().rename(columns={'station_id':'start station id'})

    n=len(stations) # get count of station ids
    stations['datetime']=pd.to_datetime(pd.Series([datetime_]*n))

    stations['dayofweek']=stations['datetime'].dt.dayofweek
    stations['hour']=stations['datetime'].dt.hour
    stations['min']=stations['datetime'].dt.minute
    stations['season']=stations['datetime'].dt.month.apply(lambda x: 'winter' if x <=2 else 'spring' if x<=5 else \
        'summer' if x<=8 else 'fall' if x<=11 else 'winter')

    # re-order columns
    stations=stations[['start station id','season','dayofweek','hour','min']]

    # Dummify seasons
    le = LabelEncoder()
    stations['season'] = le.fit_transform(stations['season'])


    # load bike demand model
    rf_model = load('/Volumes/5TB EXT Drive/rfc_bike.joblib')
    prediction_bike=rf_model.predict(stations)

    # load dock demand model
    rf_model = load('/Volumes/5TB EXT Drive/rfc_dock.joblib')
    stations=stations.rename(columns={'start station id': 'end station id'})
    prediction_dock=rf_model.predict(stations)

    stationid = stations[['end station id']].rename(columns={'end station id':'station_id'})
    prediction_bike = pd.DataFrame(prediction_bike, columns=['bike_demand'])
    prediction_dock = pd.DataFrame(prediction_dock, columns=['dock_demand'])

    df=pd.concat([stationid,prediction_bike,prediction_dock], axis=1)

    return df
