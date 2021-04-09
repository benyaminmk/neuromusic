# neuromusic
Auralization of brain waves

## Getting started
I recomned using conda to create an environment specific to this project. To build a new conda env,
```basj
$ conda create --name neuromusic python=3.8
$ conda activate neuromusic
$ pip install -r requirements.txt
```

## Real time auralization and plotting
If you have a muse headset, you can change the address to match your headset and then run
```bash
python realtime_auralization.py
```

## Visualize recordings
To see what was recorded and some basic features go to `data/initial_exploration.ipynb`. There's already some data saved so go ahead and check that out now! 