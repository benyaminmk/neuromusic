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

def playback_features():
    """replay recorded episode. 
    Both raw EEG data and extracted features can be played back.

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
        time.sleep(dt.seconds-0.6)
        t_0=t



def playback_raw(window_length,window_step): #TODO variable sliding window to explore tempo
    dt = RAW.time.values[0] - RAW.time.diff()[1]
    for idx, datapoint in RAW.iterrows():
        t=datapoint.time
        yield datapoint
        dt = t-t_0
        time.sleep(dt.seconds)
        t_0=t

if __name__ == "__main__":
    print('playing episode with realtime dynamics\n')
    for datapt in playback_episode():
        print(datapt)