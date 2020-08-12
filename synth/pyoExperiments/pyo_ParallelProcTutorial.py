from pyo import *

s = Server().boot()
s.amp = 0.1     # reduce amplitude by 20dB

a = Sine()      # Create sinve wave as source to process

#   processing objects (the ones that modify an audio source), have a first argument called "input"
#   which specifies the audio to be processed
hr = Harmonizer(a).out()    # Pass Sine through a Harmonizer
ch = Chorus(a).out()        # Pass Sine through a Chorus
sh = FreqShift(a).out()     # Pass Sine through a Frequency Shifter

s.gui(locals())     # Initiate GUI