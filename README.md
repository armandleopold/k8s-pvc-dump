# k8s-pvc-dump
Python script that dumps in tar.gz PVCs in Kubernetes cluster

## Run it : 

You will need to set 3 env variables :
* DUMP_DIR : The directory that will contains your dumps
* PVC_DIR : The directory that contains your PVCs
* DUMP_INTERVAL : The interval in which you want that dumps occures.

There is an auto garbage collector that follows the schema :

Keeping dumps that have date from : 
- 1/1/currentYear-1
- 1/1/currentYear
- 1/currentMonth-1
- 21/currentMonth
- 14/currentMonth
- 7/currentMonth
- 1/currentMonth
- currentDay-1
- currentDay

Throwing everything else.

So you will have at maximum 9 DUMPS from every PVCs you have.
If we imagine having a compression Ratio of 10, then you can calculate that you need approxymately the same amount of storage for PVCs and for Dumps.