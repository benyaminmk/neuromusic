from pyo import *
import time

s = Server().boot()
s.amp = 0.1

s.start()

env = Adsr(attack=0.01, decay=0.2, sustain=0, release=0.1, dur=2, mul=0.5)

osc1 = Sine(mul=env).out()

base = 27.5      # reference base note

scale = {}

for i in range(88):
    scale[i] = base * 2 ** (i / 12)

    osc1.freq = scale[i]
    
    print(f'{i + 21} --> {scale[i]}')

    env.play()

    time.sleep(0.1)

s.stop()