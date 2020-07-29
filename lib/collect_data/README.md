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
right now the data collected is saved locally in `data/`