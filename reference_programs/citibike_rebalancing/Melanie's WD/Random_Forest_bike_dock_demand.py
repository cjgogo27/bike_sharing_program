
import pandas as pd
import numpy as np
import pickle
from joblib import dump, load
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

outgoingDF = pd.read_pickle("../Data/outgoingDF.pkl")
incomingDF = pd.read_pickle("../Data/incomingDF.pkl")


######################### Bike Demand Model #######################
X=outgoingDF
X['dayofweek']=pd.to_datetime(X.starttime_date).dt.dayofweek
temp=X.starttime_interval.str.split(":",expand=True)
temp.columns=['hour','min']
temp['hour']=temp['hour'].astype('int32')
temp['min']=temp['min'].astype('int32')
X=pd.merge(X,temp,left_index=True, right_index=True)

X=X.drop(columns=['starttime_date','starttime_interval','outgoing_bike_count','bike_demand'])
y=outgoingDF['bike_demand']

# Label Encoding
le = LabelEncoder()
X['season'] = le.fit_transform(X['season'])


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

clf = RandomForestClassifier(random_state=0, verbose=True, n_jobs=-1)
clf.fit(X_train, y_train)
dump(clf, 'rfc_bike.joblib') 


######################### Dock Demand Model #######################
X=incomingDF
X['dayofweek']=pd.to_datetime(X.stoptime_date).dt.dayofweek
temp=X.stoptime_interval.str.split(":",expand=True)
temp.columns=['hour','min']
temp['hour']=temp['hour'].astype('int32')
temp['min']=temp['min'].astype('int32')
X=pd.merge(X,temp,left_index=True, right_index=True)

X=X.drop(columns=['stoptime_date','stoptime_interval','incoming_bike_count','dock_demand'])
y=incomingDF['dock_demand']

# Label Encoding
le = LabelEncoder()
X['season'] = le.fit_transform(X['season'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

rfc = RandomForestClassifier(random_state=0, n_jobs=-1)
rfc.fit(X_train, y_train)
dump(rfc, 'rfc_dock.joblib') 