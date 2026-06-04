############################################# Overview #############################################
# Script to process CitiBike station data downloaded from https://www.theopenbus.com/raw-data.
# Original datasets were tab-deliminated monthly datasets with inconsistent numbers of columns, so
# they couldn't be read and combined directly with Python without some sort of processing. Each year's 
# monthly files were combined at the command line level and saved to  a yearly file in the format 
# "stations{year}.csv" - once this was accomplished, the files were fed through the below script to 
# separate the tab-delimitors, standardize the columns, and then combine data from all years into a
# single .csv file.
####################################################################################################

import pandas as pd

# Define a function to process station data from a given year
def process_yearlydata(year):
    temp = pd.read_csv(f"./stationdata/stations{year}.csv")

    # Generate the list of columns to be used. Assign the temporary dataframe a placeholder column name
    colnames = temp.columns[0].split('\t')
    temp.columns = ['_']

    # Split dataframe into multiple columns and save that to a new temporary dataframe
    temp_expanded = temp['_'].str.split("\t", expand = True)

    # Drop any unnecessary columns created by the splitting
    if temp_expanded.shape[1]>13:
        temp_expanded.drop(list(range(13, temp_expanded.shape[1])), axis = 1, inplace = True)
    
    # Assign the correct column names to the dataframe and write it to disk
    temp_expanded.columns = colnames[0:13]
    temp_expanded.to_csv(f"./stationdata/stations{csvfile}.csv", index = False)    


# Apply the above function to all data
years = [i for i in range(2015, 2020)]
process_yearlydata(year)


# Read in the processed datafiles and concatenate them into a single dataframe
stations2015 = pd.read_csv("./stationdata/stations2015.csv")
stations2016 = pd.read_csv("./stationdata/stations2016.csv")
stations2017 = pd.read_csv("./stationdata/stations2017.csv")
stations2018 = pd.read_csv("./stationdata/stations2018.csv")
stations2019 = pd.read_csv("./stationdata/stations2019.csv")

allstations = pd.concat([stations2015, stations2016, stations2017, stations2018, stations2019])


# Write the final concatenated dataframe to disk
allstations.to_csv("./allstations.csv", index = False)