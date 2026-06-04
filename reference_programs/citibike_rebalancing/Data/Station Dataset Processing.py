import pandas as pd
import numpy as np
import re

stations = pd.read_csv("./allstations.csv")
stations_processed = stations.copy()

##### Drop rows where the values are physically impossible or contain 
stations_processed.dropna(inplace = True)
stations_processed.drop(stations_processed[stations_processed['dock_id'].apply(lambda x: isinstance(x, str))].index, inplace = True)
stations_processed = stations_processed[stations_processed['tot_docks'] < 2000]


##### Parsing available bikes and docks
# Parsing availabile bikes
mask = ~stations_processed['avail_bikes'].astype(str).str.contains('[A-z]')
stations_processed = stations_processed[mask]
stations_processed['avail_bikes'] = stations_processed['avail_bikes'].apply(lambda x: re.sub("\"", "", str(x))) # Remove quotation marks so strings can be converted to integers later
stations_processed = stations_processed[stations_processed['avail_bikes'] != ""] # Drop any empty values
stations_processed['avail_bikes'] = stations_processed['avail_bikes'].astype(float).astype(int) # Convert strings to integers
stations_processed = stations_processed[stations_processed['avail_bikes'] <= 100] # Remove any row with an impossible number of bikes

# Parsing available docks
mask = ~stations_processed['avail_docks'].astype(str).str.contains('[A-z]')
stations_processed = stations_processed[mask]
stations_processed['avail_docks'] = stations_processed['avail_docks'].apply(lambda x: re.sub("\"", "", str(x))) # Remove quotation marks so strings can be converted to integers later
stations_processed = stations_processed[stations_processed['avail_docks'] != ""] # Drop any empty values
stations_processed['avail_docks'] = stations_processed['avail_docks'].astype(float).astype(int) # Convert strings to integers
stations_processed = stations_processed[stations_processed['avail_docks'] <= 100] # Remove any row with an impossible number of docks


##### Parse date column into datetime format
stations_processed['date'] = pd.to_datetime(stations_processed['date'], format = '"%y-%m-%d"')


##### Convert numeric columns from strings to integers/floats as appropriate
stations_processed['dock_id'] = stations_processed['dock_id'].astype(int)
stations_processed['tot_docks'] = stations_processed['tot_docks'].astype(int)
stations_processed['minute'] = stations_processed['minute'].astype(int)

# Clean up latitude column
stations_processed['_lat'] = stations_processed['_lat'].apply(lambda x: float(re.sub('\"', "", str(x))))
# Clean up longitude column
stations_processed['_long'] = stations_processed['_long'].apply(lambda x: re.sub('[^-^.0-9]', "", str(x))).apply(lambda x: re.sub("-{2}", "-", str(x)))
stations_processed = stations_processed[stations_processed['_long'] != ""]
stations_processed['_long'].astype(float)

# Clean up hours column
stations_processed['hour'] = stations_processed['hour'].apply(lambda x: re.sub('[^0-9]', "", str(x))).astype(int)
# Convert hours to 24-hour time
stations_processed['hour'].loc[stations_processed['pm'] == 1] = stations_processed['hour'].loc[stations_processed['pm'] == 1] + 12


##### Convert minutes to half hour increments
stations_processed['minute'] = stations_processed['minute'].apply(lambda x: '00' if x < 30 else '30')


##### Remove quotations from dock name
stations_processed['dock_name'] = stations_processed['dock_name'].apply(lambda x: str(re.sub('\"', "", x)))


##### Create a depletion status column
stations_processed['depletion_status'] = (stations_processed['avail_bikes']/stations_processed['tot_docks']).apply(lambda x: "Full Risk" if x > 2/3 else "Empty Risk" if x < 1/3 else "Healthy")


##### Drop unnecessary columns
stations_processed.drop(['pm', 'in_service', 'status_key'], axis = 1, inplace = True)


##### Create new columns (variables for the combined time, day of the week, and season of the observation)
stations_processed = stations_processed.assign(time = lambda x: x['hour'].astype(str) + ":" + x['minute'].astype(str))
stations_processed = stations_processed.assign(dayofweek = lambda x: x['date'].dt.weekday)
stations_processed = stations_processed.assign(season = lambda x: x['date'].dt.month.apply(
	lambda y: 'winter' if y <= 2 else 'spring' if y <= 5 else 'summer' if y <= 8 else 'fall' if y <= 11 else 'winter'))


##### Write the file to a .csv for later use
stations_processed.to_csv("./allstations_processed.csv", index = False)




