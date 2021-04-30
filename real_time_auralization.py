""" Author: Benyamin Meschede-Krasa 
stream real-time EEG and convert it to audio """
import os
import subprocess
import time
from threading import Thread

import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi, firwin
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pylsl import StreamInlet, resolve_byprop
from lib.collect_data import bci_workshop_tools as BCIw

import pyo
from synth.constants import scales

#########################
##### GLOBAL PARAMS #####
#########################

FEATURES = ['delta', 'theta', 'alpha', 'beta', 'gamma']


class EEG_stream():
    def __init__(self, 
                 muse_address="00:55:DA:B7:74:0D",
                 buffer_length = 15, 
                 epoch_length = 2, 
                 overlap_length = 0.8,
                 feature_names=None,
                 filter_state=None):
        
        # init attributes
        self.buffer_length = buffer_length
        self.epoch_length = epoch_length
        self.overlap_length = overlap_length

        self.shift_length = epoch_length - overlap_length
        # connect muse headset
        subprocess.Popen(["python",
                                              "-u",
                                                os.path.join('lib','collect_data','muse-lsl.py'), #run the muse-lsl.py script
                                                "--address",
                                                muse_address])
                                    
        #give it time to connect to the headset
        time.sleep(10)

        self._init_lsl_stream()
        self._init_eeg_buffer(feature_names,filter_state)
        # self._init_viz()

        
    def _init_lsl_stream(self):
        # Search for active LSL stream
        print('Looking for an EEG stream...')
        streams = resolve_byprop('type', 'EEG', timeout=2)
        if len(streams) == 0:
            raise RuntimeError('Can\'t find EEG stream.')

        # Set active EEG stream to inlet and apply time correction
        print("Start acquiring data")
        self.inlet = StreamInlet(streams[0], max_chunklen=12)
        eeg_time_correction = self.inlet.time_correction()

        # Get the stream info and description
        info = self.inlet.info()
        description = info.desc()
        self.fs = int(info.nominal_srate())
        self.n_channels = info.channel_count()

        ch = description.child('channels').first_child()
        ch_names = [ch.child_value('label')]
        for i in range(1, self.n_channels):
            ch = ch.next_sibling()
            ch_names.append(ch.child_value('label'))
        self.ch_names = ch_names
    
    def _init_eeg_buffer(self,feature_names,filter_state):
        # Index of the channel (electrode) of the head set:
        # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
        self.index_channel = [0, 1, 2, 3] #TODO This should be a parameter
        # Name of our channels for plotting purposes
        self.ch_names = [self.ch_names[i] for i in self.index_channel]
        self.n_channels = len(self.index_channel)
        
        #TODO check if this should be here !!
        if feature_names is None:
            self.feature_names = BCIw.get_feature_names(self.ch_names)
        elif isinstance(feature_names, (list,np.ndarray, pd.core.series.Series)):
            self.feature_names = feature_names
        else:
            raise TypeError(f"`feature_names` must be array_like, got {feature_names} which is type {type(feature_names)}")

        # Initialize raw EEG data buffer (for plotting)
        self.eeg_buffer = np.zeros((int(self.fs * self.buffer_length), self.n_channels)) #TODO n_channels may have to be shortened to be jsut EEG which is the first 4 channels so n_channels[:4]
        self.filter_state = filter_state  # for use with the notch filter
        
        #TODO clean
        # # Compute the number of epochs in "buffer_length" (used for plotting)
        # n_win_test = int(np.floor((buffer_length - epoch_length) /
        #                             shift_length + 1))
        

        # Initialize the feature data buffer (for plotting)
        self.feat_buffer = np.zeros((1,len(FEATURES)))

    # def _init_viz(self):
    #     # Initialize the plots
    #     # self.plotter_eeg = BCIw.DataPlotter(self.fs * self.buffer_length, self.ch_names, self.fs)

    #     # could also plot spectral features if that's desired.
    #     self.plotter_features = BCIw.DataPlotter(1, FEATURES, 1 / self.shift_length)

    def update_buffer(self):
        ######### ACQUIRE  RAW DATA #########

        # Obtain EEG data from the LSL stream
        eeg_data, timestamp = self.inlet.pull_chunk(
                timeout=1, max_samples=int(self.shift_length * self.fs))
        epoch_dict={}

        if not bool(eeg_data):
            raise RuntimeError('Can\'t find EEG stream.')
        # Only keep the channel we're interested in
        ch_data = np.array(eeg_data)[:, self.index_channel]
        
        # Update EEG buffer
        self.eeg_buffer, self.filter_state = BCIw.update_buffer(
                self.eeg_buffer, ch_data, notch=True,
                filter_state=self.filter_state)

    def compute_features(self):
        # Get newest samples from the buffer
        self.data_epoch = BCIw.get_last_data(self.eeg_buffer,
                                        self.epoch_length * self.fs)


        # Compute features
        feat_vector = BCIw.compute_feature_vector(self.data_epoch,self.fs)
        self.feat_buffer, _ = BCIw.update_buffer(self.feat_buffer,feat_vector.values)

        return feat_vector

    # def update_viz(self):
    #     # self.plotter_eeg.update_plot(self.eeg_buffer)
    #     self.plotter_features.update_plot(self.feat_buffer)
    #     plt.pause(0.00001)
    
class Synth():
    def __init__(self,
                 scale='pentatonic', #I think this is only working on scales with 12 values
                 n_octaves = 1,
                 attack=0.01,
                 decay=0.3, 
                 sustain=1, 
                 release=0.1,
                 dur=2, 
                 mul=0.5,
                 base=55,
                 oct_offset=4,
                 chr_offset=0):
        
        self.scale = np.hstack([np.hstack(scales[scale]) + i*12 for i in len(n_octaves)]) #TODO
        self.base = base
        self.oct_offset = oct_offset
        self.chr_offset = chr_offset
        # self.scale_step_alpha = self.scale_step_gamma = 0 #TODO clean
        
        self.server = pyo.Server().boot()
        self.server.start()

        self.env = pyo.Adsr(attack=attack, 
                            decay=decay, 
                            sustain=sustain, 
                            release=release,
                            dur=dur, 
                            mul=mul)
        
        self.osc_alpha = pyo.Sine(mul=self.env).out()
        self.osc_gamma = pyo.Sine(mul=self.env).out()

    def step_scales(self,scale_step_alpha,scale_step_gamma):
        def step(osc,scale_step):
            osc.freq = float((self.base + self.base * self.oct_offset) * 2 ** ((scale_step + self.chr_offset) / 12)) 

        self.scale_step_alpha = scale_step_alpha
        self.scale_step_gamma = scale_step_gamma

        step(self.osc_alpha, self.scale_step_alpha)
        step(self.osc_gamma,self.scale_step_gamma)
    
    def play(self):
        self.env.play()

class Plotter():
    def __init__(self,  window=5., scale=100., figsize=[15,6],dejitter=True,subsample=2,filt=True):
        """Init"""
        self.window = window
        self.scale = scale
        self.dejitter = dejitter
        self.subsample = subsample
        self.filt = filt

        streams = resolve_byprop('type', 'EEG', timeout=2)
        if len(streams) == 0:
            raise RuntimeError('Can\'t find EEG stream.')
        self.stream=streams[0]
        self.inlet = StreamInlet(streams[0], max_chunklen=12)


        info = self.inlet.info()
        description = info.desc()

        self.sfreq = info.nominal_srate()
        self.n_samples = int(self.sfreq * self.window)
        self.n_chan = info.channel_count()

        ch = description.child('channels').first_child()
        ch_names = [ch.child_value('label')]

        for i in range(self.n_chan):
            ch = ch.next_sibling()
            ch_names.append(ch.child_value('label'))

        self.ch_names = ch_names

        fig, axes = plt.subplots(1, 1, figsize=figsize, sharex=True)
        fig.canvas.mpl_connect('key_press_event', self.OnKeypress)
        fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.fig = fig
        self.axes = axes

        sns.despine(left=True)

        self.data = np.zeros((self.n_samples, self.n_chan))
        self.times = np.arange(-self.window, 0, 1./self.sfreq)
        impedances = np.std(self.data, axis=0)
        lines = []

        for ii in range(self.n_chan):
            line, = axes.plot(self.times[::self.subsample],
                              self.data[::self.subsample, ii] - ii, lw=1)
            lines.append(line)
        self.lines = lines

        axes.set_ylim(-self.n_chan + 0.5, 0.5)
        ticks = np.arange(0, -self.n_chan, -1)

        axes.set_xlabel('Time (s)')
        axes.xaxis.grid(False)
        axes.set_yticks(ticks)

        ticks_labels = ['%s - %.1f' % (ch_names[ii], impedances[ii])
                        for ii in range(self.n_chan)]
        axes.set_yticklabels(ticks_labels)

        self.display_every = int(0.2 / (12/self.sfreq))

        # self.bf, self.af = butter(4, np.array([1, 40])/(self.sfreq/2.),
        #                          'bandpass')

        self.bf = firwin(32, np.array([1, 40])/(self.sfreq/2.), width=0.05,
                         pass_zero=False)
        self.af = [1.0]

        zi = lfilter_zi(self.bf, self.af)
        self.filt_state = np.tile(zi, (self.n_chan, 1)).transpose()
        self.data_f = np.zeros((self.n_samples, self.n_chan))

    def update_plot(self):
        k = 0
        while self.started:
            samples, timestamps = self.inlet.pull_chunk(timeout=1.0,
                                                        max_samples=12)
            if timestamps:
                if self.dejitter:
                    timestamps = np.float64(np.arange(len(timestamps)))
                    timestamps /= self.sfreq
                    timestamps += self.times[-1] + 1./self.sfreq
                self.times = np.concatenate([self.times, timestamps])
                self.n_samples = int(self.sfreq * self.window)
                self.times = self.times[-self.n_samples:]
                self.data = np.vstack([self.data, samples])
                self.data = self.data[-self.n_samples:]
                filt_samples, self.filt_state = lfilter(
                    self.bf, self.af,
                    samples,
                    axis=0, zi=self.filt_state)
                self.data_f = np.vstack([self.data_f, filt_samples])
                self.data_f = self.data_f[-self.n_samples:]
                k += 1
                if k == self.display_every:

                    if self.filt:
                        plot_data = self.data_f
                    elif not self.filt:
                        plot_data = self.data - self.data.mean(axis=0)
                    for ii in range(self.n_chan):
                        self.lines[ii].set_xdata(self.times[::self.subsample] -
                                                 self.times[-1])
                        self.lines[ii].set_ydata(plot_data[::self.subsample, ii] /
                                                 self.scale - ii)
                        impedances = np.std(plot_data, axis=0)

                    ticks_labels = ['%s - %.2f' % (self.ch_names[ii],
                                                   impedances[ii])
                                    for ii in range(self.n_chan)]
                    self.axes.set_yticklabels(ticks_labels)
                    self.axes.set_xlim(-self.window, 0)
                    self.fig.canvas.draw()
                    k = 0
            else:
                time.sleep(0.2)

    def onclick(self, event):
        print((event.button, event.x, event.y, event.xdata, event.ydata))

    def OnKeypress(self, event):
        if event.key == '/':
            self.scale *= 1.2
        elif event.key == '*':
            self.scale /= 1.2
        elif event.key == '+':
            self.window += 1
        elif event.key == '-':
            if self.window > 1:
                self.window -= 1
        elif event.key == 'd':
            self.filt = not(self.filt)

    def start(self):
        self.started = True
        self.thread = Thread(target=self.update_plot)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.started = False


def aurilize_neuro(feature_vector,alpha_quantiles,gamma_quantiles):
    
    # TODO get from feat_vector
    alpha = None
    gamma = None

    alpha_quantile_index = np.argmin(np.abs(np.array(alpha_quantiles)-float(feature_vector.alpha)))
    scale_step_alpha = alpha_quantiles[alpha_quantile_index]

    gamma_quantile_index = np.argmin(np.abs(np.array(gamma_quantiles)-float(feature_vector.gamma)))
    scale_step_gamma = gamma_quantiles[gamma_quantile_index]

    return scale_step_alpha, scale_step_gamma

if __name__ == "__main__":
    ######################
    ######  PARAMS  ######
    ######################
    alpha_qt = []
    gamma_qt=[]
    for qt in np.linspace(0,1,len(scale)):
        quantile_all = data_generator.FEATS.quantile(qt)
        alpha_qt.append(quantile_all.alpha)
        gamma_qt.append(quantile_all.gamma)
    
    # 12 quantiles of alpha data collected on myself
    ALPHA_QUANTILES = [-0.7550127559323341, 
                        1.3198856619998833, 
                        2.1707540555600264, 
                        2.738749286090746, 
                        3.3545093627816485, 
                        3.7946102796451284, 
                        4.395034043531364, 
                        5.005569836480687, 
                        6.000723144932735, 
                        7.833779831600835, 
                        11.310411755616798, 
                        23.678368915514415]
    
    # 12 quantiles of alpha data collected on myself
    GAMMA_QUANTILES = [-12.542292838087715, 
                       -12.081162295340171, 
                       -11.889595880567683, 
                       -11.76731350029794, 
                       -11.668818547418061, 
                       -11.564513681924069, 
                       -11.45097337667895, 
                       -11.268980527059625, 
                       -10.988518451426957, 
                       -9.616172288483565, 
                       -6.733267291300871, 
                       -2.8179178487023138]
    
    
    ####################
    ######  MAIN  ######
    ####################
    stream = EEG_stream()
    synth = Synth()

    # run the plotter at the same time
    subprocess.Popen(['python','-u','realtime_plotter.py'])
    try:
        while True:
            # update eeg buffer and get new features
            stream.update_buffer()
            feature_vector = stream.compute_features()
            # stream.update_viz()

            # convert eeg feature into scale step for aurilization
            scale_step_alpha, scale_step_gamma = aurilize_neuro(feature_vector, ALPHA_QUANTILES, GAMMA_QUANTILES)
            synth.step_scales(scale_step_alpha, scale_step_gamma)
            synth.play()
    except KeyboardInterrupt:
        synth.server.stop()



