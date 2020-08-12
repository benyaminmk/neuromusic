from pyo import *
import time

s = Server().boot()
s.start()

sf = SfPlayer(SNDS_Path + '/transparent.aif', loop=True, mul=.3).out()
harm = Harmonizer(sf, transpo=7, winsize=0.05).out(1)

time.sleep(5)
s.stop()
time.sleep(0.25)
s.shutdown()