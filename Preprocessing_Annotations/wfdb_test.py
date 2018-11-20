from IPython.display import display
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import glob
import ntpath
import numpy as np
import os
import shutil

import wfdb

def testOpenApneaECG():
    db_path = 'datasets\\db1_apnea-ecg\\a01';
    #db_path = 'physionet.org\\ucddb002';

    record = wfdb.rdrecord(db_path)
    #wfdb.plot_wfdb(record=record, title='Record a1 from Physionet Apnea')

    ann = wfdb.rdann(db_path, 'apn')
    print(ann.sample)
    print(ann.symbol)

    wfdb.plot_wfdb(record=record, annotation=ann, plot_sym=True, title='Record a1 from Physionet Apnea')
    return;

def testOpenUCDDB(filepath):
    path = "physionet.org\\ucddb002";
    record = wfdb.rdrecord(path, 'rec');
    return;

def testOpenSHHSPSDB():
    path = 'shhpsgdb\\0000';
    record = wfdb.rdrecord(path);
    wfdb.plot_wfdb(record=record, plot_sym=True, title='shhpsdb Record ' + path)
    print(record);
    return

def ucddbResampleAnnotation(source_file, target_file):

    # read relevant columns
    times = []
    types = []
    durations = []
    with open(source_file, "r") as file:
        i = 0;
        for line in file:
            if i > 2: # ignore first three rows
                colums = line.split(' ');
                colums = [x for x in colums if x != '']

                if len(colums) > 3: # check if line is valid
                    date_time = datetime.strptime(colums[0], '%H:%M:%S')
                    times.append(date_time);
                    types.append(colums[1]);

                    # handle thr column "PB"
                    if colums[2].isdigit():
                        durations.append(float(colums[2]));
                    elif colums[3].isdigit():
                        durations.append(float(colums[3]));
                    else:
                        durations.append(float(colums[4]));
            i+=1
    print(times);
    print(types);
    print(durations);

    # do the resampling
    print('do resampling')
    times_resampled = [];
    types_resampled = [];

    for i in range(len(times)):
        time_add_duration = times[i] + timedelta(seconds=durations[i]); # add duration to time
        #times_resampled.append(time_add_duration.replace(second=0)) # round down to full minute
        if time_add_duration.minute != times[i].minute:
            times_resampled.append(times[i].replace(second=0));
            types_resampled.append('(-)');
            times_resampled.append(time_add_duration.replace(second=0));
            types_resampled.append(types[i]);
        else:
            times_resampled.append(time_add_duration.replace(second=0))
            types_resampled.append(types[i]);

    print(times_resampled);
    print(types_resampled)

    # write resampled annotations into new file
    with open(target_file, "w+") as file:
        file.write('-\n')
        file.write('-\n')
        file.write("Time\tType\n");
        print(len(times_resampled));
        print(len(types_resampled));
        for i in range(len(times_resampled)):
            file.write(times_resampled[i].strftime('%H:%M:%S') + '\t' + types_resampled[i] + '\n');
    return;

def ucddbResampleAnnotationAll():
    for path in glob.glob("physionet.org/*_respevt.txt"):
        file_name = ntpath.basename(path);
        ucddbResampleAnnotation('physionet.org\\'+file_name, 'physionet.org\\AnnotationsResampled\\Resampled_' + file_name);
    return;

#testOpenSHHSPSDB();
#ucddbResampleAnnotationAll();
testOpenApneaECG();