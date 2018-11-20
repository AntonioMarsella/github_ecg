from collections import Counter;
import math;
from datetime import datetime

def IsFirstApneaOverlapInterval(intervall):
    """
    Check is this intervall can be seen as a "first overlap interval". This function is used to handle overlaps (regarding intervalls) of apnea occurences.
    :param intervall: List with apnea indicators (0 and 1)
    :return:
    """

    if 0 in intervall:
        last_element = 1;
        for element in reversed(intervall):
            if last_element == 0 and element == 1:
                return  False; # rising edge detected! this intervall cannot be marked as "no apnea".
            last_element = element
    else:
        # all elements are 1 => cannot be marked as "no apnea"
        return False;

    return True; # else this intervall can be maked as "no apnea" (if the next intervall contains apnea)

# this is a core function for resampling annotations
def ResampleAnnotations(annotations, source_sample_frequency, target_sample_frequency, preserve_input_size=True, ignore_first_timeframe_during_overlap=True, ignore_short_apnea_in_timeframe=False):
    """
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

    resampled_annotations = [];

    # check frequencies
    if target_sample_frequency == source_sample_frequency:
        # If the target is the same as the source frequency, do nothing
        resampled_annotations = annotations;
    elif target_sample_frequency < source_sample_frequency:
        # downsample:

        time_frame = int(source_sample_frequency / target_sample_frequency);

        number_time_frames = math.ceil(len(annotations)/float(time_frame));

        for i in range(number_time_frames):
            start_pos = int(i*time_frame);
            end_pos = int(start_pos + time_frame);
            elements_in_timeframe = annotations[start_pos:end_pos:1];

            if 1 in elements_in_timeframe:
                resampled_annotations.extend([1]);
            else:
                resampled_annotations.extend([0]);

            if ignore_first_timeframe_during_overlap == True:
                if i > 0 and resampled_annotations[i] == 1:
                    # starting from the second intervall and if the current intervall is marked as "apnea", check the last intervall, if it can be makred with "no apnea"
                    last_interval = annotations[start_pos - time_frame: end_pos - time_frame];
                    if IsFirstApneaOverlapInterval(last_interval):
                        resampled_annotations[i-1] = 0;

    else:
        # upsamlpe: This case makes only sense if preserve_input_size = False
        x = 0;

    if preserve_input_size:
        resampled_annotations_input_size = []
        for element in resampled_annotations:
            dublicated_element = [element] * int(time_frame);
            resampled_annotations_input_size.extend(dublicated_element);
        resampled_annotations = resampled_annotations_input_size;

    return resampled_annotations

def UCDDB_LoadAnnonationsTXTFileRaw(source_file):
    """
    Database 3: https://physionet.org/pn3/ucddb/
    Read Annotations from file as is (signals are not sampled/equidistant)
    :param source_file: File path to annotations file
    :return:
    """
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
    return (times, types);

def UCDDB_LoadAnnonationsTXTFileResampled(source_file, start_time, duration_in_seconds, target_frequency=1):
    """
    Reads and resamples the annotations in a file. F.ex. the annotations in the file are just written, if apnea had occured.
    Non-Apnea cases are now added so that all datapoints are equidistant and correspond to the actual time (f.ex. 1Hz for second precision).
    :param source_file: File path
    :param start_time: Starting time of the experiment
    :param duration_in_seconds: Duration of the experiment
    :param target_frequency: Freqiency of apnea signal (default 1Hz for one datapoint per second)
    :return: resampled time and types (apnea) signals
    """
    (raw_times, raw_types) = UCDDB_LoadAnnonationsTXTFileRaw(source_file);

    full_time = []
    full_type = []


    return (raw_times, raw_types);