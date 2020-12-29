import os
import sys
import pause
import shutil
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta
from tabulate import tabulate

def getFolderSize(root_directory = "."):
    return sum(f.stat().st_size for f in Path(root_directory).glob('**/*') if f.is_file())

def convert_bytes(num):
    step_unit = 1000.0 #1024 bad the size

    for x in ['octets', 'Ko', 'Mo', 'Go', 'To']:
        if num < step_unit:
            return "%3.1f %s" % (num, x)
        num /= step_unit
        
def path_to_df(root_directory = "."):
    files = []
    for path in Path(root_directory).iterdir():
        info = path.stat()
        
        size = ""
        byte_size = 0
        
        if(path.is_file()):
            size = convert_bytes(info.st_size)
            byte_size = info.st_size
        elif(path.is_dir()):
            size = convert_bytes(getFolderSize(str(path)))
            byte_size = getFolderSize(str(path))

        files.append({'path':str(path),
                      'size':size,
                      'byte_size':byte_size,
                      'created':datetime.fromtimestamp(info.st_ctime).strftime("%d-%m-%Y"),
                      'modified':datetime.fromtimestamp(info.st_mtime).strftime("%d-%m-%Y"),
                      'is_dir':str(path.is_dir())})
    return pd.DataFrame(files)

# This algo return true or false if we need to drop dumps
def dumpToDrop(date):
    currentYear = int(now.strftime("%Y"))
    currentMonth = int(now.strftime("%m"))
    currentDay = int(now.strftime("%d"))
    
    drop = False
    
    if(date != "1-1-"+str(currentYear-1)
    and (date != "1-1-"+str(currentYear))
    and (date != "1-"+str(currentMonth-1)+"-"+str(currentYear))
    and (date != "21-"+str(currentMonth)+"-"+str(currentYear))
    and (date != "14-"+str(currentMonth)+"-"+str(currentYear))
    and (date != "7-"+str(currentMonth)+"-"+str(currentYear))
    and (date != "1-"+str(currentMonth)+"-"+str(currentYear))
    and (date != str(currentDay-1)+"-"+str(currentMonth)+"-"+str(currentYear))
    and (date != str(currentDay)+"-"+str(currentMonth)+"-"+str(currentYear))):
        drop = True
        
    return drop

author = "Armand LEOPOLD"
scriptVersion  = "0.1"
execution = 0

print("########################################################")
print("## K8S PVC DUMP | Author "+author+" | Version "+scriptVersion+" ##")
print("########################################################\n")
print("----> Get Environment variables")
try:
    DUMP_DIR = str(os.environ.get('DUMP_DIR'))
    PVC_DIR = str(os.environ.get('PVC_DIR'))
    DUMP_INTERVAL = str(os.environ.get('DUMP_INTERVAL'))
    
    print("DUMP_DIR : "+DUMP_DIR)
    print("PVC_DIR : "+PVC_DIR)
    print("DUMP_INTERVAL : "+DUMP_INTERVAL)
except:
    print("[ERROR] Cant't fetch env variables :", sys.exc_info()[0])
    raise
    
## Come back here
while(True):
    execution += 1
    skip = False
    now = datetime.now()
    interval = datetime.now() + timedelta(seconds=int(DUMP_INTERVAL))

    print("########################################################")
    print("## Execution N°"+str(execution))
    print("Execution date and time : "+now.strftime("%d/%m/%Y %H:%M:%S"))

    print("----> Listing files in PVC_DIR")
    pvcdf = path_to_df(PVC_DIR)
    if(len(pvcdf) == 0):
        print("[WARNING] No pvc to dump in the location. Will try tomorrow.")
        skip = True
    else:
        print(tabulate(pvcdf, headers='keys', tablefmt='psql', showindex=False))
        print("----> Listing files in DUMP_DIR")
        dumpdf = path_to_df(DUMP_DIR)
        print(tabulate(dumpdf, headers='keys', tablefmt='psql', showindex=False))
        print("----> Has been restarted ?")
        if(len(dumpdf) == 0):
            print("No dumps yet") 
        else:
            if(datetime.now().strftime("%d-%m-%Y") == dumpdf['modified'].max()):
                print("There are Dumps from Today, so we have likely been restarted. Skipping dumping for today.")
                skip = True

        print("----> Has enought disk space for dumping ?")

        total, used, free = shutil.disk_usage(DUMP_DIR)
        print("Total: %d Go" % (total // (2**30)))
        print("Used: %d Go" % (used // (2**30)))
        print("Free: %d Go" % (free // (2**30)))

        if(pvcdf['byte_size'].sum()*0.8 > free):
            print("Not enought disk space left.")
            skip = True
        else:
            print("Enought space.")

    if(not skip):
        print("## We are Go for dumping.")
        for i in range(0,len(pvcdf)):
            pvcName = pvcdf.iloc[i]['path'].split('/')[-1]
            print("Dumping : "+pvcName+" | size : "+pvcdf.iloc[i]['size'])
            shutil.make_archive(DUMP_DIR+"/"+pvcName+"_"+now.strftime("%d-%m-%Y"), 'gztar',pvcdf.iloc[i]['path'])

        print("## Done.")
        print("## Checking dumps to erase.")
        dumpdf = path_to_df(DUMP_DIR)
        dumpdf['tobedel'] = dumpdf['created'].apply(dumpToDrop)
        print(tabulate(dumpdf, headers='keys', tablefmt='psql', showindex=False))
        deletionList = list(dumpdf['path'][dumpdf['tobedel'].astype(bool) & ~dumpdf['is_dir'].map({'True': True, 'False': False})])
        print("DUMPS to be deleted : "+str(deletionList))
        for dumpToDelete in deletionList:
            try:
                os.remove(str(dumpToDelete))
                print('Dropped : '+str(dumpToDelete))
            except:
                print("[ERROR] Cant't delete dump !", sys.exc_info()[0])

    print("----> Next Execution date :"+interval.strftime("%d/%m/%Y %H:%M:%S"))
    print("Going to sleep. zZZz")
    pause.until(interval)
