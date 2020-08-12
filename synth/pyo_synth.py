from pyo import *   # Pyo synth. Install using:     python -m pip install pyo
import sys, time

##----- Define quantized piano frequencies -----##
base = 27.5         # Define a base frequency
chrmScale = {}      # Create empty dict to store all the chromatic scale frequencies

for i in range(88):
    chrmScale[i] = base * 2 ** (i/12)       # Extract frequencies of all 88 piano notes
    print(f'{i + 21} --> {chrmScale[i]}')


##----- Initialize audio server -----##
s = Server().boot()
s.amp = 0.1         # Set sever amplitude
s.start()           # Start audio server

##----- Initialize audio components -----##
env = Adsr(attack=1, release=2, dur=0, mul=1)  # Env with soft attack and release, undetermined duration, and amplitude mult at full gain
osc1 = Sine(mul=env).out()          # Oscillator 1 in stereo with a sinewave.


##----- Working code -----##
while True:
    x = input('select MIDI note between 21 and 108: ')  # Prompt user for input

    if x.isalpha():             # Break loop if input is not numeric
        break

    x = int(x)                  # Cast input as integer

    if x < 21 or x > 108:       # Break loop if input is outside specified range
        break

    osc1.freq = chrmScale[x - 21]           # Assign frequency to oscillator 1
    env.play()                              # Play envelope

    time.sleep(1)                           # Reprompt after 1 second

##----- Stop audio and audio server -----##
env.stop()
time.sleep(3)
print('Audio stopped')
s.stop()