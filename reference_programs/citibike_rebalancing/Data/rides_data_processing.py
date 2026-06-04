# Using Dask to parallel process large pandas dataframe.
# Aggregate bike/dock demands in a 30 minute interval.

import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import swifter # for fast pandas.apply

stations = pd.read_csv('../Data/live_stations.csv') # all stations after '2019-12-01'
sampledd = dd.read_csv('../Data/all_combined.csv', parse_dates=['starttime','stoptime'],\
dtype={'start station id': 'Int32', 'end station id': 'Int32'}) # load all data into Dask dataframe

sampledd.starttime.astype('M8[us]')
sampledd.stoptime.astype('M8[us]')

# create new columns from dates columns
sampledd['year']=sampledd.starttime.dt.year 
sampledd['starttime_date']=sampledd.starttime.dt.date
sampledd['stoptime_date']=sampledd.stoptime.dt.date
sampledd['starttime_hour']=sampledd.starttime.dt.hour
sampledd['stoptime_hour']=sampledd.stoptime.dt.hour
sampledd['starttime_min']=sampledd.starttime.dt.minute
sampledd['stoptime_min']=sampledd.stoptime.dt.minute
sampledd['starttime_min']=sampledd['starttime_min'].apply(lambda x: '00' if x < 30 else '30', \
    meta=pd.Series(dtype='str', name='starttime_min'))
sampledd['stoptime_min']=sampledd['stoptime_min'].apply(lambda x: '00' if x < 30 else '30', \
    meta=pd.Series(dtype='str', name='stoptime_min'))
sampledd['starttime_interval']=sampledd.apply(lambda x: str(x['starttime_hour'])+":"+str(x['starttime_min']), axis=1, \
    meta=pd.Series(dtype='str', name='starttime_interval'))
sampledd['stoptime_interval']=sampledd.apply(lambda x: str(x['stoptime_hour'])+":"+str(x['stoptime_min']), axis=1, \
    meta=pd.Series(dtype='str', name='stoptime_interval'))
sampledd['season']=sampledd.starttime.dt.month.apply(lambda x: 'winter' if x <=2 else 'spring' if x<=5 else \
    'summer' if x<=8 else 'fall' if x<=11 else 'winter',meta=pd.Series(dtype='str', name='season'))
sampledd['dayofweek']=sampledd['starttime'].dt.weekday.apply(lambda x: 'Monday' if x==0 else 'Tuesday' if x==1 else \
    'Wednesday'if x==2 else 'Thursday' if x==3 else 'Friday' if x==4 else 'Saturday' if x==5 else 'Sunday', \
        meta=pd.Series(dtype='str', name='dayofweek'))

# Drop stations not live as of 12/1/2019
# Drop 2020 rides
# Drop midnight to 6am rides
sampledd=sampledd[sampledd['start station id'].isin(stations.station_id.unique().tolist())]
sampledd=sampledd[sampledd['end station id'].isin(stations.station_id.unique().tolist())]
sampledd=sampledd[sampledd['year']!=2020]
sampledd=sampledd[sampledd['starttime_hour']>=6]

# aggregate bike/dock demands in a 30 minute interval.
with ProgressBar():
    outgoingDF=sampledd.groupby(['start station id','starttime_date','season','dayofweek','starttime_interval']).\
        count()[['starttime']].reset_index().rename(columns={'starttime':'outgoing_bike_count'}).compute(scheduler="processes")
    incomingDF=sampledd.groupby(['end station id','stoptime_date','season','dayofweek','stoptime_interval'])\
        [['stoptime']].count().reset_index().rename(columns={'stoptime':'incoming_bike_count'}).compute(scheduler="processes")

outgoingDF['bike_demand']=outgoingDF.swifter.apply(lambda x: 'High' if x['outgoing_bike_count']> outgoingDF.outgoing_bike_count.describe()['75%'] else \
    'Medium' if x['outgoing_bike_count']>outgoingDF.outgoing_bike_count.describe()['25%'] else 'Low', axis=1)
incomingDF['dock_demand']=incomingDF.swifter.apply(lambda x: 'High' if x['incoming_bike_count']>4 else \
    'Medium' if x['incoming_bike_count']>1 else 'Low', axis=1) # 75 percentile is 4 and 25 percentile is 1.

# save results.
outgoingDF.to_pickle("../Data/outgoingDF.pkl")
incomingDF.to_pickle("../Data/incomingDF.pkl")