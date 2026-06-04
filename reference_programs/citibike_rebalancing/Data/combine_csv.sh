#!/bin/bash

head -1 ../temp/201501-citibike-tripdata.csv > all_combined.csv
tail -n +2 -q ../temp/*.csv >> all_combined.csv