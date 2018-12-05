from IPython.display import display
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import glob
import ntpath
import numpy as np
import os
import shutil
import csv

import wfdb
import Preprocessing_Annotations.ApneaPreprocessing as ap

def OpenApneaECG():
    db_path = 'datasets\\db1_apnea-ecg\\a01';
    #db_path = 'datasets\\db3_ucddb\\ucddb002';

    record = wfdb.rdrecord(db_path)

    signals, fields = wfdb.rdsamp(db_path)
    print('Fields: ', fields)

    ann = wfdb.rdann(db_path, 'apn')
    print("ann.sample len = ", len(ann.sample))
    print(ann.sample)

    print("ann.symbol len = ", len(ann.symbol))
    print(ann.symbol)

    wfdb.plot_wfdb(record=record, annotation=ann, plot_sym=True, title='Record a1 from Physionet Apnea')
    return

def OpenUCDDB():
    record_path = 'D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb\\Record100Hz\\ucddb002_lifecard_100Hz'
    annotation_path = 'D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb\\ResampledAnn100HzRecord\\ucddb002_lifecard_100Hz_Shorter_IgnoreOverlap'
    record = wfdb.rdrecord(record_path)

    signals, fields = wfdb.rdsamp(record_path)
    print('Fields: ', fields)

    print('counter_freq', record.counter_freq)
    print('samples_per_frame', record.samps_per_frame)

    ann = wfdb.rdann(annotation_path, 'apn')
    print("ann.sample len = ", len(ann.sample))
    print(ann.sample)

    print("ann.symbol len = ", len(ann.symbol))
    print(ann.symbol)

    wfdb.plot_wfdb(record=record, annotation=ann, plot_sym=True, title=record_path)
    return

def OpenUCDDB_1():
    db_path = 'D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb\\ResamplesRecord100Hz\\ucddb002_100Hz';

    record = wfdb.rdrecord(db_path)

    signals, fields = wfdb.rdsamp(db_path)
    print('Fields: ', fields)

    wfdb.plot_wfdb(record=record, plot_sym=True, title=db_path)
    return

def UCDDB_Functions():
    path = 'datasets\\db3_ucddb\\ucddb002_respevt.txt';

    apnea_signals = ap.UCDDB_LoadAnnonationsTXTFileRaw(path);
    print(apnea_signals);

    start_time = datetime.strptime('00:11:04', '%H:%M:%S')
    annotations_std = ap.UCDDB_LoadAnnonationsTXTFileStandardized(path, start_time=start_time, duration_in_seconds=7.65*60*60);
    print(annotations_std)

    annotations_std_binary = [not(type=='none') for type in annotations_std]

    resampled = ap.ResampleAnnotations(
        annotations=annotations_std_binary,
        source_sample_frequency=1,
        target_sample_frequency=(1 / 60),
        preserve_input_size=False,
        ignore_first_timeframe_during_overlap=False,
        ignore_short_apnea_in_timeframe=False)

    resampled_full_size = ap.ResampleAnnotations(
        annotations=annotations_std_binary,
        source_sample_frequency=1,
        target_sample_frequency=(1 / 60),
        preserve_input_size=True,
        ignore_first_timeframe_during_overlap=False,
        ignore_short_apnea_in_timeframe=False)

    resampled_full_size_IgnoreFirstOverlap = ap.ResampleAnnotations(
        annotations=annotations_std_binary,
        source_sample_frequency=1,
        target_sample_frequency=(1 / 60),
        preserve_input_size=True,
        ignore_first_timeframe_during_overlap=True,
        ignore_short_apnea_in_timeframe=False)

    plt.plot(resampled)

    apn_symbols = list()
    for element in resampled:
        symbol = 'N'
        if element == 1:
            symbol = 'A'
        apn_symbols.append(symbol)

    resampled_1Min = [element*60*128 for element in range(len(apn_symbols))]

    print('Write annotation file')
    print(resampled_1Min)
    print(apn_symbols)
    wfdb.wrann('ucddb002', 'apn', np.array(resampled_1Min), np.array(apn_symbols))

    with open('datasets\\db3_ucddb\\AnnotationsResampled\\ucddb002_AnnotationsInfo.txt', mode='w', newline='') as csv_file:
        fieldnames = \
            ['Sample',
             'DateTime',
             'Apnea yes/no',
             'Apnea Type',
             'Apnea yes/no Resampled',
             'Apnea yes/no Resampled Ignore First Overlap'
             ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')

        writer.writeheader()

        for i in range(len(annotations_std)):
            writer.writerow({'Sample': i,
                             'DateTime': (start_time + timedelta(seconds=i)),
                             'Apnea yes/no': annotations_std_binary[i],
                             'Apnea Type': annotations_std[i],
                             'Apnea yes/no Resampled': resampled_full_size[i],
                             'Apnea yes/no Resampled Ignore First Overlap': resampled_full_size_IgnoreFirstOverlap[i]
                             })

    return

def OpenSHHSPSDB():
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

# ap.ResampleRecordFile(
#     record_source_dir = 'D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb',
#     record_source_name = 'ucddb002',
#     record_target_dir = 'D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb\\ResamplesRecord100Hz',
#     record_target_name = 'ucddb002_100Hz',
#     target_frequency=100
# )

# ap.ResampleRecordFiles(
#     record_source_dir='D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb',
#     record_target_dir='D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb\\ResamplesRecord100Hz',
#     target_frequency=100
# )

OpenUCDDB()

# ap.UCDDB_ResampleAnnotations(
#     path_source='D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb\\Record100Hz',
#     path_target ='D:\\SkyDrive\\Studium\\Maastricht\\Project1\\Period2ResampleAnnotations\\datasets\\db3_ucddb\\ResampledAnn100HzRecord',
#     target_file_postfix='_Shorter_IgnoreOverlap',
#     source_file_portfix='_lifecard_100Hz',
#     preserve_input_size=False,
#     ignore_first_timeframe_during_overlap=True,
#     create_annotationfiles_as_ascii=False,
#     print_log=True
# )