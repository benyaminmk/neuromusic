""" Author: Benyamin Meschede-Krasa 
play back saved data in order to build systems offline """
import os
import pandas as pd

######################
######  PARAMS  ######
######################
DIR_DATA = os.path.join('..','data')
FP_FEATS = os.path.join(DIR_DATA, 'trial_features.feather')

#############################
######  PRECONDITIONS  ######
#############################
assert os.path.isdir(DIR_DATA)
assert os.path.isfile(FP_FEATS)

# load saved features
FEATS = pd.read_feather(FP_FEATS)

def playback_episode(episode=FEATS):
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
    for idx, datapoint in episode.iterrows():
        yield datapoint

