#   pyo session 2

from pyo import *
import time

s = Server().boot()

#   LFO for frequency modulation of oscillator a
mod = Sine(freq=6, mul=50)

a = Sine(freq=mod + 440, mul=0.1).out()

s.gui(locals())