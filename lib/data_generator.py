""" Author: Benyamin Meschede-Krasa 
play back saved data in order to build systems offline """
import os
import time
import pandas as pd

######################
######  PARAMS  ######
######################

DIR_DATA = os.path.join(os.path.dirname(__file__),'..','data')
FP_FEATS = os.path.join(DIR_DATA, 'trial_features.feather')
FP_RAW = os.path.join(DIR_DATA, 'trial_raw.feather')

#############################
######  PRECONDITIONS  ######
#############################
assert os.path.isdir(DIR_DATA)
assert os.path.isfile(FP_FEATS)
assert os.path.isfile(FP_RAW)

# load saved features
FEATS = pd.read_feather(FP_FEATS)
RAW = pd.read_feather(FP_RAW)
SFREQ = int(1/(RAW.time[1] - RAW.time[0]))

def playback_features():
    """
    Generator that simulates a data stream of EEG spectral band features in 
    real time from pre-reorded data.

    Parameters
    ----------
    episode : dataframe, optional
        dataframe containing eith EEG data or extracted features
        Each row is what is generated in real time,
        by default `trial_features.feather`

    Yields
    -------
    datapoint: pd.Series
        series containing data packet equivalent to what is 
        outputted when collecting data online
        Contents of datapoint depends on episode (raw eeg or features)
    """
    t_0 = FEATS.time.values[0] - FEATS.time.diff()[1]
    for idx, datapoint in FEATS.iterrows():
        t=datapoint.time
        yield datapoint
        dt = t-t_0
        time.sleep(dt.seconds)
        t_0=t



def playback_raw(window_length,window_step): #TODO variable sliding window to explore tempo
    """Generator that simulates a real-time stream of EEG data in it's
    raw format with flexible sliding window parameters. Based on playback
    of pre-recorded data.

    Parameters
    ----------
    window_length : float
        length of each data window in seconds
    window_step : float
        amount the sliding window moves forward with each step, in seconds

    Yields
    -------
    window : pandas.DataFrame
        window of EEG data from 4 channels (uV) plus time in seconds
    """
    if window_step>window_length: print(f"WARNING: window step ({window_step}) is greater than window length ({window_length}) which means data between windows is dropped")
    n_windows = (len(RAW)-window_length*SFREQ)//int(window_step*SFREQ)
    
    for i in range(n_windows):
        start_idx = int(window_step*SFREQ)*i
        stop_idx = int(window_step*SFREQ)*i + int(window_length*SFREQ)
        window = RAW.iloc[start_idx:stop_idx]
        yield window
        time.sleep(window_step)

if __name__ == "__main__":
    ## PARAMS
    WINDOW_LENGTH = 3 # seconds
    WINDOW_STEP = 0.5 # seconds

    ## MAIN
    print('playing episode spectral band features with realtime dynamics\n')
    for datapt in playback_features():
        print(datapt)

    print(f'playing back same episode but raw data (window length: {WINDOW_LENGTH} window step: {WINDOW_STEP} with realtime dynamics\n')

    for win in playback_raw(window_length=WINDOW_LENGTH,window_step=WINDOW_STEP):
        print(win.head())
