import os
import sys
import random
import time
import pyo
import constants
import numpy as np

sys.path.append(os.path.join(os.path.abspath(''),"..","lib"))
import data_generator

######################
#### SERVER SETUP ####
######################
# s is the server instance
s = pyo.Server().boot()
s.start()

#####################
#### SYNTH SETUP ####
#####################
env = pyo.Adsr(attack=0.01, decay=0.3, sustain=1, release=0.1,
           dur=2, mul=0.5
)
osc_alpha = pyo.Sine(mul=env).out()
osc_gamma = pyo.Sine(mul=env).out()
################
#### PARAMS ####
################
base_alpha = 55           # reference base note in Hz (A1 = 55Hz)
base_gamma = 55
oct_offset = 4      # octave offset
chr_offset = 0      # chromatic offset
scale = constants.scales["chromatic"]
scale_step_alpha = scale_step_gamma = 0


#########################
#### NEURO --> SOUND ####
#########################
# find quantiles for each spectral band
# during playback, see which value it is nearest to an play the scale note associated with that quantile index
alpha_qt = []
gamma_qt=[]
for qt in np.linspace(0,1,len(scale)):
    quantile_all = data_generator.FEATS.quantile(qt)
    alpha_qt.append(quantile_all.alpha)
    gamma_qt.append(quantile_all.gamma)

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
    return quantiles[quantile_index]


for data_point in data_generator.playback_episode():
    # output_note (in Hz) = base * 2 ** (i / 12)
    # where i is the number of half steps above the base
    osc_alpha.freq = float((base_alpha + base_alpha * oct_offset) * 2 ** ((scale_step_alpha + chr_offset) / 12))
    osc_gamma.freq = float((base_gamma + base_gamma * oct_offset) * 2 ** ((scale_step_gamma + chr_offset) / 12))

    print("ALPHA SYNTH")
    print(f"Scale step:\t{scale_step_alpha}")
    print(f"Frequency:\t{osc_alpha.freq}\n")
    print("GAMMA SYNTH")
    print(f"Scale step:\t{scale_step_gamma}")
    print(f"Frequency:\t{osc_gamma.freq}\n")

    env.play()

    scale_step_alpha = get_closest_quantile(data_point.alpha, alpha_qt)
    scale_step_gamma = get_closest_quantile(data_point.gamma, gamma_qt)
s.stop()
