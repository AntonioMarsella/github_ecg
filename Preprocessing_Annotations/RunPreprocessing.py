import glob
import Preprocessing_Annotations.ApneaPreprocessing as ap

datasets = sorted(glob.glob('D:\\GitRepositories\\DSDM\\Period1\\github_ecg\\db_shhs\\edfs\\shhs1\\*.edf'))
ap.createRepresentationChunks(
    paths_datasets=datasets,
    dir_target ='D:\\GitRepositories\\DSDM\\Period1\\github_ecg\\db_shhs\\edfs\\shhs1\\Scalograms',
    database=2,
    target_freq=100, # must be 100, can't be changed (!)
    sample_seconds=60, # must be 60, can't be changed (!)
    print_log=True
)


# its assumed that the .dat, .hea and .apn files are in the same directory
# the apnea files have the postfix '_Shorter_IgnoreOverlap'
# f.ex.: ucddb002_lifecard_100Hz.dat, ucddb002_lifecard_100Hz.hea,  ucddb002_lifecard_100Hz_Shorter_IgnoreOverlap.apn

datasets = sorted(glob.glob('D:\GitRepositories\DSDM\Period1\github_ecg\db3_ucddb\Resampled\Record100Hz\\*.dat'))
ap.createRepresentationChunks(
    paths_datasets=datasets,
    dir_target ='D:\GitRepositories\DSDM\Period1\github_ecg\db3_ucddb\Resampled\Record100Hz\\Scalograms',
    database=3,
    target_freq=100, # must be 100, can't be changed (!)
    sample_seconds=60, # must be 60, can't be changed (!)
    print_log=True
)