### A Machine Learning project to predict rebalancing needs for citibike docks.
##### <i>Purpose: Given a date and time, for each CitiBike station, predict outgoing bike demand, incoming bike demand and depletion status. Use the predictions to generate paired list of stations to/ from which to move bikes to ensure maximum rider fulfillment.
#### <i>Data</i>
- The anymonous trip system data: https://www.citibikenyc.com/system-data.
- Weather information from noaa: https://www.ncei.noaa.gov/data/global-hourly/archive/csv/.
- Dock-station bike stocking information: https://www.theopenbus.com/raw-data.html.

- combine_csv.sh : bash script that combines all downloaded rides data into one massive csv file.
- rides_data_processing.py : script that takes one massive rides data into two datasets, outgoingDF and incomingDF.
- outgoingDF.zip
- incomingDF.zip
- stations_distance.py : script that calculates for every station, the distance to every other stations. Result is saved in station_dict.pkl.

#### <i>Model</i>
- Random_Forest_bike_dock_demand.py : Script to generate Random Forest models for Bike Demand and Dock Demand.
- predict_bike_dock_demand.py : Given datetime, predict bike demand and dock demand for all stations.
- predict_station_status.py : Given datetime, predict station status for all stations. 
- rebalancing : Only script to run that generates rebalancing strategy. Given datetime, merges bike demand, dock demand, station status and predict the nearest stations to rebalance to and from.
After generating the respective random forest models and saved in .joblib format, run the following script to generate rebalancing recommendations.
```bash
(base) Melanies-MacBook-Pro:citibike_rebalancing melaniezheng$ cd Models/
(base) Melanies-MacBook-Pro:Models melaniezheng$ python rebalancing.py '2020-07-17 9:00'
```
These rfc models are to huge to be uploaded to github. Please follow Model/Random_Forest_bike_dock_demand.py or christianopperman/ for further info and steps to regenerate.
- rfc_bike.joblib
- rfc_dock.joblib
- depletion_status_classifier.joblib

#### <i>Results</i>
- rebalancing results in csv files with respective datetime in the filename.

