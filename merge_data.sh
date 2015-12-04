#!/bin/bash

for year in `seq 1981 2015`
do
    mkdir $year
    cp gsod_$year.tar $year/
    cd $year
    tar -xf gsod_$year.tar
    for file in `ls *.gz`
    do
	gunzip $file
	data_file=`echo $file | cut -d '.' -f1,2`
	sed -i '1d' $data_file
	cat $data_file >>$'all-stations_'$year.txt
    done
    hdfs dfs -copyFromLocal "all-stations_$year.txt" /users/wfvining/weather_data/
    rm ./*.op
    cd ..
done
