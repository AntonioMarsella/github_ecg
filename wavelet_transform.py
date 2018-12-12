import numpy as np
import matplotlib.pyplot as plt


import pywt
import wfdb

import os.path



time, sst = pywt.data.nino()

db_path = '/home/michael/Projects/ECGSleepApnea/www.physionet.org/physiobank/database/apnea-ecg/'

DATA_A_SIZE = 20
DATA_B_SIZE = 5
DATA_C_SIZE = 10
DATA_X_SIZE = 35
CHUNK_SIZE = 6000

patient_groups = {'a' : DATA_A_SIZE, 'b' : DATA_B_SIZE, 'c' : DATA_C_SIZE}

for k in patient_groups:
    for i in range(1, patient_groups[k]+1):
        filename = str(k + '%02d' % i)
        full_path_to_filename = str(db_path + filename)
        ann = wfdb.rdann(full_path_to_filename, 'apn')
        ann_i = 0
        record = wfdb.rdrecord(full_path_to_filename)
        record_len = record.sig_len
        last_chunk_index = int(np.floor(record_len/CHUNK_SIZE))*CHUNK_SIZE
        for j in range(0,record_len,CHUNK_SIZE):
            current_chunk_size=CHUNK_SIZE
            sampto_index = j + current_chunk_size
            if j==last_chunk_index:
                current_chunk_size=record_len-last_chunk_index
                sampto_index= j + current_chunk_size

            if j // CHUNK_SIZE < ann.ann_len:
                    ann_i = j // CHUNK_SIZE

            fname = '/home/michael/Projects/ECGSleepApnea/cwt_classes_jpgs/' + ann.symbol[ann_i] + '/' + filename + '_' + str(j) + '.jpg'

            if not os.path.isfile(fname):
                sst, fields = wfdb.rdsamp(full_path_to_filename, sampfrom = j, sampto = sampto_index)
                sst = sst.flatten()

                dt = 0.01

                wavelet = 'cmor1.5-1.0'
                scales = np.arange(1, 125)
                frequencies = pywt.scale2frequency(wavelet, scales) / dt


                [cfs, frequencies] = pywt.cwt(sst, scales, wavelet)
                frequencies = pywt.scale2frequency(wavelet, scales) / dt

                #plt.imshow(cfs, cmap='PRGn', aspect='auto', vmax=abs(cfs).max(), vmin=-abs(cfs).max())
                #plt.show()

                power = (abs(cfs)) ** 2
                plt.ioff()

                f, ax = plt.subplots(figsize=(15, 10))
                time = range(0, current_chunk_size)
                ax.contourf(time, frequencies, power)

                # f.patch.set_visible(False)
                # ax.axis('off')



                name = '/home/michael/Projects/ECGSleepApnea/cwt_classes_jpgs/' + ann.symbol[ann_i] + '/' + filename + '_' + str(j) + '.jpg'
                f.savefig(fname)
                plt.close(f)

