# k8s-pvc-dump
Python script that dumps in tar.gz PVCs in Kubernetes cluster

Prerequisites :
* Python 3.3+
* Dependencies :
    * pandas
    * tabulate
    * pause

## Run it : 

You will need to set 3 env variables :
* DUMP_DIR : The directory that will contain your dumps.
* PVC_DIR : The directory that contains your PVCs.
* DUMP_INTERVAL : The interval in which you want that dumps occures (in seconds). (CAN'T BE MORE THAN 86200 (1 DAY))

There is (an auto garbage collector) or Embeded cleanup policy for those who are more familiar with artifact repository managment, that follows the following scheme :

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

## Docker image : 

