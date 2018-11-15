import numpy as np
import matplotlib.pyplot as plt


import pywt
import wfdb

time, sst = pywt.data.nino()

db_path = './'

DATA_A_SIZE = 20
DATA_B_SIZE = 5
DATA_C_SIZE = 10
CHUNK_SIZE = 6000

patient_groups = {'a' : DATA_A_SIZE, 'b' : DATA_B_SIZE, 'c' : DATA_C_SIZE}

for k in patient_groups:

    for i in range(1, patient_groups[k]+1):

        filename = str(db_path + k + '%02d' % i)
        record = wfdb.rdrecord(filename)
        record_len = record.sig_len
        last_chunk_index = int(np.floor(record_len/CHUNK_SIZE))*CHUNK_SIZE
        for j in range(0,record_len,CHUNK_SIZE):
            current_chunk_size=CHUNK_SIZE
            sampto_index = j + current_chunk_size
            if j==last_chunk_index:
                current_chunk_size=record_len-last_chunk_index
                sampto_index= j + current_chunk_size


            sst, fields = wfdb.rdsamp(filename, sampfrom = j, sampto = sampto_index)
            sst = sst.flatten()

            dt = 0.01

            # Taken from http://nicolasfauchereau.github.io/climatecode/posts/wavelet-analysis-in-python/
            wavelet = 'cmor1.5-1.0'
            scales = np.arange(1, 125)

            [cfs, frequencies] = pywt.cwt(sst, scales, wavelet)
            power = (abs(cfs)) ** 2

            f, ax = plt.subplots(figsize=(15, 10))
            time = range(0, current_chunk_size)
            ax.contourf(time, np.log2(frequencies), power)
            f.savefig('./cwt/' + filename + '_' + str(j) + '.png')
            plt.close(f)
