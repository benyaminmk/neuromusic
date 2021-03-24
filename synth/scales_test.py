import random
import time

from pyo import *

import constants

######################
#### SERVER SETUP ####
######################
# s is the server instance
s = Server().boot()
s.start()

#####################
#### SYNTH SETUP ####
#####################
env = Adsr(attack=0.01, decay=0.3, sustain=0, release=0.1,
           dur=2, mul=0.5
)
osc1 = Sine(mul=env).out()

################
#### PARAMS ####
################
base = 55           # reference base note in Hz (A1 = 55Hz)
oct_offset = 4      # octave offset
chr_offset = 0      # chromatic offset
scale = constants.scales["chromatic"]
scale_step = 0


while True:
    # output_note (in Hz) = base * 2 ** (i / 12)
    # where i is the number of half steps above the base
    osc1.freq = (base + base * oct_offset) * 2 ** ((scale_step + chr_offset) / 12)

    print(f"Scale step:\t{scale_step}")
    print(f"Frequency:\t{osc1.freq}")

    env.play()

    time.sleep(0.2)

    scale_step = random.choice(scale)

s.stop()
