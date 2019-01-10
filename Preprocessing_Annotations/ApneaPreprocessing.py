from collections import Counter
import os
import math
import datetime
from datetime import datetime
from datetime import timedelta
import glob
from pathlib import Path
import pyedflib
import xml.etree.ElementTree

import numpy as np
import csv

import wfdb
import wfdb.processing

import pywt
import matplotlib
import matplotlib.pyplot as plt
from halo import Halo

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

# NOT NEEDED
def ResampleRecordFile(record_source_dir, record_source_name, record_target_dir, record_target_name, target_frequency):
    '''
    Creates a new record file with a new frequency. Uses wfdb functions
    :param record_source_name: path to source record (no extension)
    :param record_target_name: path to target record (no extension)
    :param target_frequency: in Hz
    :return:
    '''

    # Read part of a record from Physiobank
    record_source_path = record_source_dir + '\\' + record_source_name

    signals, fields = wfdb.rdsamp(record_source_path)

    print('Record to resample', record_source_path)
    print(fields)
    print('Original signal shape', np.shape(signals))

    # see docs:  https://wfdb.readthedocs.io/en/latest/processing.html#wfdb.processing.resample_sig
    signals = np.transpose(signals) # transpose, so that to following loop works
    resampled_signals = [wfdb.processing.resample_sig(signal, fields['fs'], target_frequency)[0] for signal in signals]
    resampled_signals = np.transpose(resampled_signals) # transpose back, so wfdb.wrsamp() works

    print('resampled signal shape', np.shape(resampled_signals))

    # Write a local WFDB record
    units = fields['units']
    signal_names = [name.replace(" ", "_") for name in  fields['sig_name']] # replace possible whitespaces
    fmt = ['16'] * len(units) # fmt: I don't know what this does exactly, and what to configure...

    wfdb.wrsamp(record_name= record_target_name,
                write_dir=record_target_dir,
                fs=target_frequency,
                units=units,
                sig_name=signal_names,
                p_signal=resampled_signals,
                fmt=fmt)

    return

def ResampleRecordFiles(record_source_dir, record_target_dir, target_frequency):
    '''
    Resamples alle records (.dat) in a directory (annotations are ignored).
    :param record_source_dir:
    :param record_target_dir:
    :param target_frequency:
    :return:
    '''

    # get all record files in the source folder
    record_paths = glob.glob(record_source_dir + '\\*.dat');
    # get record names (just name, not path) without file extensions
    record_names_no_extension = [Path(path).resolve().stem for path in record_paths]

    # resample all records
    for i in range(len(record_names_no_extension)):
        record_source_name = record_names_no_extension[i]
        record_target_name =str(record_source_name)+'_'+ str(target_frequency)+'Hz'
        ResampleRecordFile(
            record_source_dir=record_source_dir,
            record_source_name=record_source_name,
            record_target_dir=record_target_dir,
            record_target_name=record_target_name,
            target_frequency=target_frequency
        )

    return
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
        i = 0

        datetime_last = datetime.min
        day_counter = 0

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
        source_file_portfix = '',
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

        dataset_name = datasets[dataset_i][0] + source_file_portfix # f.ex. ucddb002
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
        #annotations_std_binary = [not (type == 'none') for type in annotations_std_types]
        annotations_std_binary = [(type == 'APNEA-O') for type in annotations_std_types]
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
                 'Apnea[%]',
                 'NoApnea[%]'
                 ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')

            # Print header only in first iteration
            if dataset_i == 0:
                writer.writeheader()

            writer.writerow({'RecordName': dataset_name,
                             'Frequency': record_frequency,
                             'NumberSamples': record_length,
                             'TotalDuration[h]': round(record_duration_in_seconds/60/60,2),
                             'Apnea[%]': round(percentage_apnea, 2),
                             'NoApnea[%]': round(percentage_no_apnea,2)
                             })
            print() # new line

        #TODO
        #createScalograms()
    return
#endregion

#region SHHS Database (Database 2)

def SHHS_getEventsPerSecond(path_annotation_file):
    """
    :return an array with seconds from 0 to duration of recording as index containing all events at that second comma separated
    :param path_annotation_file:
    :return:
    """

    # works for now, but is not guaranteed to be at that index
    e = xml.etree.ElementTree.parse(path_annotation_file).getroot().findall('ScoredEvents')[0]

    totalDuration = 0
    for event in e:
        concept = event.findtext('EventConcept')
        if concept == 'Recording Start Time':
            totalDuration = (int(float(event.findtext('Duration'))))
            break

    eventsPerSecond = ["none" for x in range(totalDuration + 1)]

    for event in e:
        concept = event.findtext('EventConcept')
        # use this for all events
        if concept != 'Recording Start Time':
            # if (concept == 'Obstructive apnea|Obstructive Apnea' or concept == 'Hypopnea|Hypopnea' or concept == 'Central apnea|Central Apnea'):
            start = int(float(event.findtext('Start')))
            duration = int(float(event.findtext('Duration')))
            for i in range(0, duration):
                # dodgy fix; duration of some events apparently goes on after recording stopped..
                if (start + i) > totalDuration:
                    break
                # handle possible overlaps of events
                if eventsPerSecond[start + i] != "none":
                    eventsPerSecond[start + i] += "," + concept
                else:
                    eventsPerSecond[start + i] = concept

    return eventsPerSecond

def SHHS_CreateRepresentationChunks(
        dir_source,
        dir_target,
        print_log=True):

    ecg_chn = 3
    target_freq = 100  # sampling frequency (target)
    sample_seconds = 60  # sample seconds
    sample_length = sample_seconds * target_freq  # sample length

    datasets = sorted(glob.glob(dir_source + '\\*.edf'))
    # loop through all data sets
    for dataset_i in datasets:

        # -----------------------------------------------------------------------
        # Init
        # -----------------------------------------------------------------------

        dataset_path = dataset_i  # f.ex. ucddb028_lifecard

        print('Starting to process: ', dataset_path)

        # f.ex. MyPath\\ucddb002_respevt.txt
        annotation_source_path = dataset_path[:-4] + '-nsrr.xml'


        # f.ex. MyPath\\MySubFolder\\Resampling_AnnotationInfo.txt
        # (used to store informations about the resamlings)
        target_path_resampling_info= dir_target + '\\' + 'Resampling_AnnotationInfo.txt'

        # get the frequency and duration of the record. This may not be the best way just to get those values
        # because the signals are loaded too (unnecessary overhead), but this database is not too big...
        #signals, fields = wfdb.rdsamp(record_source_path)

        file_reader = pyedflib.EdfReader(dataset_path)  # file handle

        # Resample to 100Hz

        ecg, _ = wfdb.processing.resample_sig(
            file_reader.readSignal(ecg_chn),
            file_reader.getSampleFrequency(ecg_chn),
            target_freq)

        record_duration_in_seconds = int(np.ceil(len(ecg) / target_freq))
        num_samp = int(np.ceil(len(ecg) / sample_length))

        # get annotation types for the complete record in 1Hz
        # (one annotation per second)

        annotations_std_types = SHHS_getEventsPerSecond(annotation_source_path)

        # convert list with annotation types to a simple list with 1 and 0
        # 0 = no apnea, 1 = apnea (the apnea type does not matter)
        annotations_std_binary = [not (type == 'none') for type in annotations_std_types]
        #annotations_std_binary = [(type == 'APNEA-O') for type in annotations_std_types]
        # ---------------------------------------------------------------
        # Resampling
        # ---------------------------------------------------------------

        # resample annotations
        resampled_ann = ResampleAnnotations(
            annotations=annotations_std_binary,
            source_sample_frequency=1,
            target_sample_frequency=(1 / 60),
            preserve_input_size=False,
            ignore_first_timeframe_during_overlap=True,
            ignore_short_apnea_in_timeframe=False)


        # convert resampled annotations (1 or 0) to symbols ('A' or 'N')
        symbol_resampled_ann = [OneOrZeroToAorN(sample) for sample in resampled_ann]

        # ---------------------------------------------------------------------------------
        # Write log file with additional information
        # ---------------------------------------------------------------------------------

        dataset_name = dataset_path.split("\\")[-1][:-4]

        count_apnea = annotations_std_binary.count(1)
        count_no_apnea = annotations_std_binary.count(0)

        percentage_apnea = count_apnea/len(annotations_std_binary) * 100
        percentage_no_apnea = count_no_apnea/len(annotations_std_binary) * 100

        with open(target_path_resampling_info, mode='a+',
                  newline='') as csv_file:
            fieldnames = \
                ['RecordName',
                 'TargetFreq',
                 'NumberSamples',
                 'TotalDuration[h]',
                 'Apnea[%]',
                 'NoApnea[%]'
                 ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')

            # Print header only in first iteration
            if dataset_i == 0:
                writer.writeheader()

            writer.writerow({'RecordName': dataset_name,
                             'TargetFreq': target_freq,
                             'NumberSamples': num_samp,
                             'TotalDuration[h]': round(record_duration_in_seconds/60/60,2),
                             'Apnea[%]': round(percentage_apnea, 2),
                             'NoApnea[%]': round(percentage_no_apnea,2)
                             })
            print() # new line

        createScalograms(ecg, dataset_path, num_samp, sample_length)

    return

# endregion

def createScalograms (ecg, dataset_path, num_samp, sample_length):

    spinner = Halo(text='Processing data... 0/' + str(num_samp - 1), spinner='dots')
    spinner.start()

    # wavelets
    w_sz = 128
    h_sz = 128
    gc = 0
    for j in range(0, num_samp):
        l = j * sample_length
        h = (j + 1) * sample_length

        if j == (num_samp - 1):
            break

        sample = ecg[l:h]

        # dt = 0.01
        wavelet = 'cmor1.5-1.0'
        scales = np.arange(1, 125)
        [cfs, frequencies] = pywt.cwt(sample, scales, wavelet)
        power = (abs(cfs)) ** 2

        plt.ioff()

        f = plt.figure()
        f.set_size_inches(w_sz, h_sz)
        time = range(0, sample_length)
        plt.contourf(time, np.log2(frequencies), power)

        plt.gca().margins(0, 0)
        plt.gca().set_axis_off()
        plt.gca().xaxis.set_major_locator(matplotlib.ticker.NullLocator())
        plt.gca().yaxis.set_major_locator(matplotlib.ticker.NullLocator())
        plt.gca().set_xticklabels([])
        plt.gca().set_yticklabels([])

        directory = dataset_path[:-4] + "\\"
        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(directory + 'im' + str(gc).zfill(len(str(num_samp))) + '.png', bbox_inches='tight', pad_inches=0,
                    dpi=(128.6) / 99)
        plt.close(f)

        if ((gc + 1) % 1) == 0:
            spinner.text = 'Processing data... ' + str(gc + 1) + '/' + str(num_samp - 1)

        gc += 1

    spinner.text = 'Processing data... ' + str(num_samp - 1) + '/' + str(num_samp - 1)
    spinner.succeed()

