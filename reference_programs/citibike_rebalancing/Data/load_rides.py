import pandas as pd
import sqlite3
from pandas.io import sql
import subprocess

# In and output file paths
in_csv = 'all_combined.csv'
out_sqlite = 'citibike.sqlite'

table_name = 'allrides' # name for the SQLite database table
chunksize = 300000 # number of lines to process at each iteration

# columns that should be read from the CSV file
columns = ['tripduration','starttime','stoptime','start station id','start station name','start station latitude','start station longitude','end station id','end station name','end station latitude','end station longitude','bikeid','usertype','birth year','gender']

# Get number of lines in the CSV file
nlines = subprocess.check_output(['wc', '-l', in_csv])
nlines = int(nlines.split()[0]) 

# connect to database
cnx = sqlite3.connect(out_sqlite)

# Iteratively read CSV and dump lines into the SQLite table
for i in range(0, nlines, chunksize):  # change 0 -> 1 if your csv file contains a column header
    
    df = pd.read_csv(in_csv,  
            header=None,  # no header, define column header manually later
            nrows=chunksize, # number of rows to read at each iteration
            skiprows=i)   # skip rows that were already read
    
    # columns to read        
    df.columns = columns

    sql.to_sql(df, 
                name=table_name, 
                con=cnx, 
                index=False, # don't use CSV file index
                if_exists='append') 
cnx.close()    
