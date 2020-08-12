#   pyo session 2

from pyo import *
import time

s = Server().boot()

#   the Adsr() function creates an envelope generator
#   the dur (duration) attribute is expressed in seconds
f = Adsr(attack=0.01, decay=0.2, sustain=0.5, release=0.1, dur=2, mul=0.5)

a = Sine(mul=f).out()

f.play()

s.gui(locals())