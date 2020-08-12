#   pyo session 1

#   import everything from pyo library
#   * = everything
from pyo import *
import time

#   s holds the Server instance
#   the boot() function boots the server
#   booting the server includes:
#       - opening Audio and MIDI interfaces
#       - setup of Sample Rate and Number of Channels
s = Server().boot()

#   the start() method initiates audio processing in the server
s.start()

#   variable a stores a Sine() object, which defines a Sine wave oscillator
#   the out() method connects the oscillator's output to the audio server's outputs
#   the mul attribute defines the amplitude multiplier, which is 1 by default
#   the Sine class constructor is defined as:
#       Sine(self, freq=1000, phase=0, mul=1, add=0)
a = Sine(440, 0, 0.1).out()

time.sleep(1)

#   parameters for Sine can be set in the order in which they are defined,
#   or they can assigned by name, leaving the rest at their default value
a = Sine(freq=220, mul=0.1).out()

time.sleep(1)

#   attributes can also be modified by using the access methods
a.setFreq(880)

time.sleep(1)

a.setMul(0.05)

time.sleep(1)

#   attributes can also be set directly
a.freq = 440

time.sleep(1)

a.mul = 0.2


#   the gui() method for the Server object keeps a script running, and allows for starting/stopping the server,
#   control the output volume, and record the generated audio to a file
#   it also has an interpreter that receives commands to interact with the server
# s.gui(locals())

time.sleep(1)

#   the stop() method stops the audio processing in the server
s.stop()
