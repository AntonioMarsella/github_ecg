from collections import Counter;
import math
import datetime
from datetime import datetime
from datetime import timedelta

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
    Non-Apnea cases are now added so that all datapoints are equidistant and correspond to the actual time (in 1Hz for second precision).
    :param source_file: File path
    :param start_time: Starting time of the experiment (datetime)
    :param duration_in_seconds: Duration of the experiment
    :param target_frequency: Freqiency of apnea signal (default 1Hz for one datapoint per second)
    :return: apnea types standardized
    """
    (raw_times, raw_types, durations) = UCDDB_LoadAnnonationsTXTFileRaw(source_file)

    # init standardized signals
    full_type = ['none'] * int(duration_in_seconds) # init all elements with 'none', they will be replaced later

    for i in range(len(raw_times)):
        i_time = raw_times[i]
        i_type = raw_types[i]
        i_duration = int(durations[i])

        i_sample_index = int((i_time - start_time).total_seconds()) # get sample index (1 Hz assumed, second-difference = sample_idx)

        for j in range(i_duration):
            full_type[i_sample_index + j] = i_type

    return full_type;

# endregion