# Collect neural data via Muse headset
## 1. Connect muse
The muse headset communicates to the machine via bluetooth. `requirements.txt` at the top of this folder contains all the packages needed to connect via bluetooth. So far this has only been tested on Benyamin's desktop using a bluetooth dongle. 

To connect the headset, from this directoy (`collect_data/`) and with root privileges, run
```bash
$ make connect
```

The output should be
```
Connected
Streaming
```

## 2. Start collecting data
To start collecting new data run:
```bash
$ make collect
```
You will be prompted for a one word description of you intended activity. It will look like this

```
Describe your behavior during recording in one word
```
Type one word and hit enter. The word you choose will define the save name for the recorded EEG and features. When you are done recording press `Ctrl+C` to end data colllection and save the collected data. Right now the data collected is saved locally in `data/`. Two files are saved per recording session: raw EEG and spectral features
