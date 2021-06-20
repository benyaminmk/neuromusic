import os
import sys
import random
import time
import pyo
import constants
import numpy as np
import pandas as pd
from mne.time_frequency.multitaper import psd_array_multitaper

sys.path.append(os.path.join(os.path.abspath(''),"..","lib"))
import data_generator

################
#### PARAMS ####
################

# music parameters
base_alpha = 55           # reference base note in Hz (A1 = 55Hz)
base_beta = 110
oct_offset = 4      # octave offset
chr_offset = 0      # chromatic offset
scale = constants.scales["pentatonic2"]
scale_step_alpha = scale_step_beta = 0

note_types = [8,4,2,1] # These are the length of notes, e.g. whole, half, quarter, eights etc.
n_sixteenth_alpha = max(note_types)
n_sixteenth_beta = max(note_types)

# EEG paramters
window_length = 3 # seconds
window_step = 0.3 # seconds

# check for lag in the simulated real-time playback
DO_TIMERS = False

######################
#### SERVER SETUP ####
######################
# s is the server instance
s = pyo.Server().boot()
s.start()

#####################
#### SYNTH SETUP ####
#####################
env1 = pyo.Adsr(attack=0.1, decay=0.5, sustain=1, release=0.1,
           dur=2, mul=0.5
)

env2 = pyo.Adsr(attack=0.1, decay=0.5, sustain=1, release=0.1,
           dur=2, mul=0.5
)

mm = pyo.Mixer(outs=1, chnls=2, time=0.025)
osc_alpha = pyo.Sine(mul=env1)
osc_beta = pyo.Osc(table=pyo.TriangleTable(),mul=env2)
reverb = pyo.Freeverb(mm[0],size=[.79,.8],damp=.9,bal=.3).out()


mm.addInput(0, osc_alpha)
mm.addInput(1, osc_beta)
mm.setAmp(0,0,0.5)
mm.setAmp(1,0,0.5)

#########################
#### NEURO --> SOUND ####
#########################
# find quantiles for each spectral band

# alpha and beta are used for note selection from the above scale param
# during playback, see which value it is nearest to an play the scale note associated with that quantile index
alpha_qt = []
beta_qt = []
for qt in np.linspace(0,1,len(scale)):
    quantile_all = data_generator.FEATS.quantile(qt)
    alpha_qt.append(quantile_all.alpha)
    beta_qt.append(quantile_all.beta)

#  delta and beta are used for note type (i.e. duration/rhythm) 
# during playback, see which value it's nearest to and plat the note for the duration associated with the quantile index
    
gamma_qt=[]
delta_qt=[]
for qt in np.linspace(0,1,len(note_types)):
    quantile_all = data_generator.FEATS.quantile(qt)
    gamma_qt.append(quantile_all.gamma)
    delta_qt.append(quantile_all.delta)



def get_closest_quantile(value, quantiles):
    """given a value and a list of quantiles for the distribution from which that value was drawn, 
    get the closest quantile. 

    Parameters
    ----------
    value : float
        value of a data point
    quantiles : list(float)
        any number of quantiles for the distribution from which the quantile was drawn

    Returns
    -------
    float
        the closest quantile to the value given
    """
    quantile_index = np.argmin(np.abs(np.array(quantiles)-value))
    return quantile_index

def spectral_bands(window):
    """calculate spectral bands from a window of EEG data. Bands are mean values averaged 
    across all 4 channels with bands defined as:
        Delta: <4Hz
        Theta: 4-8Hz
        Alpha: 8-12Hz
        Beta: 12-30Hz
        Gamma: >30 Hz

    Parameters
    ----------
    window : pandas.DataFrame
        window of EEG data from 4 channels plus a `time` column
        sampling frequency is inferred from the time column.
    
    Returns
    -------
    spectral_bands : pandas.Series
        spectral band powers for the input window
    """

    # 1. Compute the power spectral density (PSD) using multitaper method
    sfreq = int(1/(window.time.values[1] - window.time.values[0])) #infer sampling frequenccy from time column
    psd, f = psd_array_multitaper(window.drop('time',axis=1).values.T,
                                 sfreq,
                                 adaptive=True, #NOTE This might be slow, can be set to False
                                 normalization='full',
                                 verbose=False)
    
    # Average of band powers
    # Delta <4
    ind_delta, = np.where(f < 4)
    delta = np.mean(psd[:, ind_delta])
    # Theta 4-8
    ind_theta, = np.where((f >= 4) & (f <= 8))
    theta = np.mean(psd[:, ind_theta])
    # Alpha 8-12
    ind_alpha, = np.where((f >= 8) & (f <= 12))
    alpha = np.mean(psd[:, ind_alpha])
    # Beta 12-30
    ind_beta = np.where((f >= 12) & (f < 30))
    beta = np.mean(psd[:, ind_beta])
    # Gamma >30
    ind_gamma = np.where(f > 30)
    gamma = np.mean(psd[:, ind_gamma])

    spectral_bands = pd.Series({'delta':delta, 
                                   'theta': theta, 
                                   'alpha': alpha,
                                   'beta' : beta, 
                                   'gamma' : gamma})


    # convert to decibles
    spectral_bands = 10*np.log10(spectral_bands)
    return spectral_bands

########################################################
######                   MAIN                     ######
########################################################


for eeg_window in data_generator.playback_raw(window_length,window_step):
    if DO_TIMERS: start = time.time()
    # calcualte spectral features from the window
    data_point = spectral_bands(eeg_window)
    # select duration based previous value of delta and gamma
    if n_sixteenth_alpha ==max(note_types):
        scale_step_alpha = scale[get_closest_quantile(data_point.alpha, alpha_qt)]
        # output_note (in Hz) = base * 2 ** (i / 12)
        # where i is the number of half steps above the base
        osc_alpha.freq = float((base_alpha + base_alpha * oct_offset) * 2 ** ((scale_step_alpha + chr_offset) / 12))
        n_sixteenth_alpha = note_types[get_closest_quantile(data_point.gamma, gamma_qt)]
        
        env1.play()
        print("ALPHA SYNTH")
        print(f"Scale step:\t{scale_step_alpha}")
        print(f"Frequency:\t{osc_alpha.freq}")
        print(f"note type: {n_sixteenth_alpha}\n")
        
    else:
        n_sixteenth_alpha +=1
    
    if n_sixteenth_beta ==max(note_types):
        scale_step_beta = scale[get_closest_quantile(data_point.beta, beta_qt)]
        osc_beta.freq = float((base_beta + base_beta * oct_offset) * 2 ** ((scale_step_beta + chr_offset) / 12))
        n_sixteenth_beta = note_types[get_closest_quantile(data_point.delta, delta_qt)]

        env2.play()
        print("beta SYNTH")
        print(f"Scale step:\t{scale_step_beta}")
        print(f"Frequency:\t{osc_beta.freq}")
        print(f"note type: {n_sixteenth_beta}\n")

        
    else:
        n_sixteenth_beta +=1
    
    if DO_TIMERS: print(f"possible lag of {time.time()-start} seconds")


s.stop()
