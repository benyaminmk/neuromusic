""" Author: Benyamin Meschede-Krasa 
Play back data stored in ../data/ as if it were being generated in real time """

from glob import glob
import os
import numpy as np
import pandas as pd
import argparse

######################
######  PARAMS  ######
######################
DIR_DATA = '../data/'
FP_FEAT_DEFAULT = DIR_DATA+'trial_features.feather'
#############################
######  PRECONDITIONS  ######
#############################
assert os.path.exists(DIR_DATA)
assert os.path.exists(FP_FEAT_DEFAULT)

class DataGenerator(object):
    #TODO
    def __init__(self,fp_features = FP_FEAT_DEFAULT):
        assert os.path.exists(fp_features), f"no file found at {fp_features}"
        self.data = pd.read_feather(fp_features)
        self.reset()
    def next(self):
        if self.index>=len(self.data):
            self.reset()
        self.index+=1
        dt = self.data.time[self.index]-self.data.time[self.index-1]
        dt = dt.total_seconds
        out = list(self.data.loc[self.index-1,:]).append(dt)
        return out

    def reset(self):
        self.index = 0
    

if __name__ == "__main__":
    #TODO argparse
    pass
