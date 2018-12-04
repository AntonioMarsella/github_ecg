from collections import Counter;
import math
import datetime
from datetime import datetime
from datetime import timedelta
import os

import numpy as np
import csv

import wfdb

# region General core functions

def IsFirstApneaOverlapInterval(intervall):
    """
    Check is this intervall can be seen as a "first overlap interval". This function is used to handle overlaps (regarding intervalls) of apnea occurences.
    :param intervall: List with apnea indicators (0 and 1)
    :return:
    """

    if 0 in intervall:
        last_element = 1
        for element in reversed(intervall):
            if last_element == 0 and element == 1:
                return  False # rising edge detected! this intervall cannot be marked as "no apnea".
            last_element = element
    else:
        # all elements are 1 => cannot be marked as "no apnea"
        return False

    return True # else this intervall can be maked as "no apnea" (if the next intervall contains apnea)

def ResampleAnnotations(annotations, source_sample_frequency, target_sample_frequency, preserve_input_size=True, ignore_first_timeframe_during_overlap=True, ignore_short_apnea_in_timeframe=False):
    """
    This is a core function for resampling annotations.
    Resamples a given signal of annotations (array of numbers) to a new frequency.
    Elements must be sampled in a defined way f.ex. 1 Hz (elements equidistant, no "gaps" between elements).

    :param annotations: List of numbers with 0 = no apnea, 1 = apnea.
    :param source_sample_frequency: Sample frequency of annotations (input)
    :param target_sample_frequency: Sample frequency of resampled annotations (output)
    :param preserve_input_size: If TRUE the resampled annotations have the same number of elements. If FALSE the number of output elements corresponds to the specified sampling frequency.
    :param ignore_first_timeframe_during_overlap: TRUE: during an overlap of apnea cases the first time frame is ignored (no apnea)
    :param ignore_short_apnea_in_timeframe: NO IMPLEMENTED YET! "Short" apnea cases in a time frame(shorter than time frame itself - no overlaps) are ignored (no apnea)
    :return:
    """

    resampled_annotations = []
    time_frame = 0;

    # check frequencies
    if target_sample_frequency == source_sample_frequency:
        # If the target is the same as the source frequency, do nothing
        resampled_annotations = annotations
    elif target_sample_frequency < source_sample_frequency:
        # downsample:

        time_frame = int(source_sample_frequency / target_sample_frequency)

        number_time_frames = math.ceil(len(annotations)/float(time_frame))

        for i in range(number_time_frames):
            start_pos = int(i*time_frame)
            end_pos = int(start_pos + time_frame)
            elements_in_timeframe = annotations[start_pos:end_pos:1]

            if 1 in elements_in_timeframe:
                resampled_annotations.extend([1])
            else:
                resampled_annotations.extend([0])

            if ignore_first_timeframe_during_overlap == True:
                if i > 0 and resampled_annotations[i] == 1:
                    # starting from the second intervall and if the current intervall is marked as "apnea", check the last intervall, if it can be makred with "no apnea"
                    last_interval = annotations[start_pos - time_frame: end_pos - time_frame]
                    if IsFirstApneaOverlapInterval(last_interval):
                        resampled_annotations[i-1] = 0

    else:
        # upsamlpe: This case makes only sense if preserve_input_size = False
        raise NotImplementedError()

    # if the input size should be preserved, the resampled signal is enlargened by
    # just duplicating the elements
    if preserve_input_size:
        resampled_annotations_input_size = []
        for element in resampled_annotations:
            dublicated_element = [element] * int(time_frame) # duplicate the sampled element and store in new list
            resampled_annotations_input_size.extend(dublicated_element)
        resampled_annotations = resampled_annotations_input_size

    return resampled_annotations

def OneOrZeroToAorN(number):
    '''
    Convert 1 to 'A' and 0 to 'N'
    :param number:
    :return:
    '''
    symbol = 'N'
    if number == 1:
        symbol = 'A'
    return symbol

#endregion

# region Database 3 (UCDDB) specific functions
def UCDDB_LoadAnnonationsTXTFileRaw(source_file):
    """
    Database 3: https://physionet.org/pn3/ucddb/
    Read Annotations (time column and apnea column) from file as is (signals are not sampled/equidistant)
    :param source_file: File path to annotations file
    :return: (time-vector, apnea-type-vector, apnea_duration)
    """
    times = []
    types = []
    durations = []
    with open(source_file, "r") as file:
        i = 0;

        datetime_last = datetime.min
        day_counter = 0;

        for line in file:
            if i > 2: # ignore first three rows
                columns = line.split(' ')
                columns = [x for x in columns if x != '']

                if len(columns) > 3: # check if line is valid
                    date_time = datetime.strptime(columns[0], '%H:%M:%S')

                    # in the file the day is not specified (just the time), so the switch from
                    # 23:59:59 to 00:00:00 needs to be handles here by counting the day and adding it
                    # afterwards to the datetime
                    if date_time < datetime_last:
                        day_counter += 1
                    datetime_last = date_time

                    date_time = date_time + timedelta(days=day_counter);
                    times.append(date_time)
                    types.append(columns[1])

                    # handle thr column "PB"
                    if columns[2].isdigit():
                        durations.append(float(columns[2]))
                    elif columns[3].isdigit():
                        durations.append(float(columns[3]))
                    else:
                        durations.append(float(columns[4]))
            i+=1
    return (times, types, durations);

def UCDDB_LoadAnnonationsTXTFileStandardized(source_file, start_time, duration_in_seconds):
    """
    Reads and standardizes the annotations in a file. F.ex. the annotations in the file are just written, if apnea had occured.
    Non-Apnea cases are now added so that all datapoints are equidistant and correspond to the actual time (here in 1Hz for second precision).
    :param source_file: File path
    :param start_time: Starting time of the experiment (datetime)
    :param duration_in_seconds: Duration of the experiment
    :param target_frequency: Freqiency of apnea signal (default 1Hz for one datapoint per second)
    :return: apnea types standardized
    """
    (raw_times, raw_types, durations) = UCDDB_LoadAnnonationsTXTFileRaw(source_file)

    # init standardized signals
    full_type = ['none'] * int(duration_in_seconds) # init all elements with 'none', they will be replaced later

    # see comment in loop
    dirty_bugfix_daySwitch_seconds = 0

    for i in range(len(raw_times)):
        i_time = raw_times[i]
        i_type = raw_types[i]
        i_duration = int(durations[i])

        i_sample_index = int((i_time - start_time).total_seconds()) # get sample index (1 Hz assumed, second-difference = sample_idx)

        # DIRTY BUGFIX, because i found it to late...
        # The switch from f.ex 23.59 to 00:00 (day + 1) is handled in UCDDB_LoadAnnonationsTXTFileRaw()
        # But that function does not handle it, if just the start time is from the day before, so this has
        # to be handled here
        if i == 0 and i_sample_index < 0:
            dirty_bugfix_daySwitch_seconds = 1 * 24 * 60 * 60 # add one day

        i_sample_index += dirty_bugfix_daySwitch_seconds # add a correction, if needed

        for j in range(i_duration):
            full_type[i_sample_index + j] = i_type

    return full_type;

def UCDDB_ResampleAnnotations(
        path_source,
        path_target,
        target_file_postfix='',
        preserve_input_size=False,
        ignore_first_timeframe_during_overlap=True,
        create_annotationfiles_as_ascii=False,
        print_log=True):

    # NAME and EXPERIMENT START are obtained manually from 'SubjectDetails.xls' and is needed for the resampling

    datasets = [
        ['ucddb002', '00:11:04'],
        ['ucddb003', '23:07:50'],
        ['ucddb005', '23:28:42'],
        ['ucddb006', '23:57:14'],
        ['ucddb007', '23:30:22'],
        ['ucddb008', '23:29:11'],
        ['ucddb009', '22:35:22'],
        ['ucddb010', '22:51:18'],
        ['ucddb011', '22:47:38'],
        ['ucddb012', '23:23:21'],
        ['ucddb013', '23:44:00'],
        ['ucddb014', '23:37:59'],
        ['ucddb015', '23:02:45'],
        ['ucddb017', '23:16:05'],
        ['ucddb018', '23:49:02'],
        ['ucddb019', '23:30:33'],
        ['ucddb020', '23:48:21'],
        ['ucddb021', '22:52:05'],
        ['ucddb022', '23:35:05'],
        ['ucddb023', '22:55:51'],
        ['ucddb024', '22:58:02'],
        ['ucddb025', '00:25:37'],
        ['ucddb026', '22:58:13'],
        ['ucddb027', '22:56:30'],
        ['ucddb028', '00:29:08'],
    ]

    # loop through all data sets

    for dataset_i in range(len(datasets)):

        # -----------------------------------------------------------------------
        # Init
        # -----------------------------------------------------------------------

        dataset_name = datasets[dataset_i][0] # f.ex. ucddb002
        experiment_start_time = datasets[dataset_i][1] #datetime as string f.ex. 23:45:34

        print('Starting to process: ', dataset_name)

        # f.ex. MyPath\\ucddb002_respevt.txt
        annotation_source_path = path_source + '\\'+  dataset_name + '_respevt.txt'

        # f.ex. MyPath\\ucddb002
        record_source_path = path_source + '\\'+ dataset_name;

        # f.ex. MyPath\\MySubFolder\\ucddb002_resampledAnn
        annotation_file_name = dataset_name + target_file_postfix

        # f.ex. MyPath\\MySubFolder\\Resampling_AnnotationInfo.txt
        # (used to store informations about the resamlings)
        target_path_resampling_info= path_target + '\\' + 'Resampling_AnnotationInfo.txt'

        # get the frequency and duration of the record. This may not be the best way just to get those values
        # because the signals are loaded too (unnecessary overhead), but this database is not too big...
        signals, fields = wfdb.rdsamp(record_source_path)

        record_length = fields['sig_len']
        record_frequency = fields['fs']
        # calculate total duration in seconds
        record_duration_in_seconds = record_length / record_frequency

        # convert string to date time
        start_time = datetime.strptime(experiment_start_time, '%H:%M:%S')

        # get annotation types (f.ex. none, HYP-C, HYP-O, APNEA-O, etc.) for the complete record in 1Hz
        # (one annotation per second)
        annotations_std_types = UCDDB_LoadAnnonationsTXTFileStandardized(
            annotation_source_path,
            start_time=start_time,
            duration_in_seconds=record_duration_in_seconds
        )

        # convert list with annotation types to a simple list with 1 and 0
        # 0 = no apnea, 1 = apnea (the apnea type does not matter)
        annotations_std_binary = [not (type == 'none') for type in annotations_std_types]

        # ---------------------------------------------------------------
        # Resampling
        # ---------------------------------------------------------------

        # resample annotations
        resampled_ann = ResampleAnnotations(
            annotations=annotations_std_binary,
            source_sample_frequency=1,
            target_sample_frequency=(1 / 60),
            preserve_input_size=preserve_input_size,
            ignore_first_timeframe_during_overlap=ignore_first_timeframe_during_overlap,
            ignore_short_apnea_in_timeframe=False)


        # convert resampled annotations (1 or 0) to symbols ('A' or 'N')
        symbol_resampled_ann = [OneOrZeroToAorN(sample) for sample in resampled_ann]


        # Generate sample indices to map the annotations to the record
        # (f.ex. if 100Hz, the indices are [0, 6000, 12000, 18000, ...]

        symbol_resampled_ann_sampleIndices = [i * 60 * record_frequency
                                                    for i in range(len(symbol_resampled_ann))]

        # ---------------------------------------------------------------------------------
        # Write annotation files
        # ---------------------------------------------------------------------------------


        print('Write annotation file into ', path_target)

        if print_log: print('Sample indices', symbol_resampled_ann_sampleIndices)
        if print_log: print('Apnea symbols', symbol_resampled_ann)
        wfdb.wrann(
            record_name= annotation_file_name ,
            extension='apn',
            sample= np.array(symbol_resampled_ann_sampleIndices),
            symbol=np.array(symbol_resampled_ann),
            write_dir=path_target
        )

        # ---------------------------------------------------------------------------------
        # Write log file with additional information
        # ---------------------------------------------------------------------------------

        count_apnea = annotations_std_binary.count(1)
        count_no_apnea = annotations_std_binary.count(0)

        percentage_apnea = count_apnea/len(annotations_std_binary) * 100
        percentage_no_apnea = count_no_apnea/len(annotations_std_binary) * 100

        with open(target_path_resampling_info, mode='a+',
                  newline='') as csv_file:
            fieldnames = \
                ['RecordName',
                 'Frequency',
                 'NumberSamples',
                 'TotalDuration[h]',
                 'PercentageApnea',
                 'PercentageNoApnea'
                 ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')

            # Print header only in first iteration
            if dataset_i == 0:
                writer.writeheader()

            writer.writerow({'RecordName': record_source_path,
                             'Frequency': record_frequency,
                             'NumberSamples': record_length,
                             'TotalDuration[h]': round(record_duration_in_seconds/60/60,2),
                             'PercentageApnea': round(percentage_apnea, 2),
                             'PercentageNoApnea': round(percentage_no_apnea,2)
                             })
            print() # new line
    return

# endregion