#!/bin/bash

STRDATE=1;
ENDDATE=5;
STRT="06:00:00";
ENDT="09:00:00";
AREA=("鹽埕區","前金區");
declare -i VEHICLENUM=2
declare MIPMAXSEC=3600
declare TRUCKCAP=14

FILENAME="$STRDATE-$ENDDATE-$MIPMAXSEC"

FUNCTION=$1;

echo -e "start info:\n=================================\nstart date : $STRDATE \
        \nend date : $ENDDATE\nstart time : $STRT\nend time : $ENDT\ntarget area : $AREA \
        \ntruck number : $VEHICLENUM\ncapacity : $TRUCKCAP\nmax time : $MIPMAXSEC sec\n" >&1 | tee log/$FILENAME.txt;

STATION_NUM=`python bss_routing.py $STRDATE $ENDDATE $STRT $ENDT $AREA $FUNCTION`

echo -e "start gurobi mip routing optimization.......\n=================================\n" >&1 | tee -a log/$FILENAME.txt;
python routing.py $VEHICLENUM $STATION_NUM $TRUCKCAP $MIPMAXSEC >&1 | tee -a log/$FILENAME.txt;

python result.py >&1 | tee -a log/mip-$MIPMAXSEC-result.txt;