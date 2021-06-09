import numpy as np

# Scales start in A
scales = {
    "chromatic":    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "pentatonic":   [0, 3, 5, 7, 10],

    # Diatonic Modes
    "ionian":       [0, 2, 4, 5, 7, 9, 11],
    "dorian":       [0, 2, 3, 5, 7, 9, 10],
    "phrygian":     [0, 1, 3, 5, 7, 8, 10],
    "lydian":       [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":   [0, 2, 4, 5, 7, 9, 10],
    "aeolian":      [0, 2, 3, 5, 7, 8, 10],
    "locrian":      [0, 1, 3, 5, 6, 8, 10],

    "har_minor":    [0, 2, 3, 5, 7, 8, 11],
    "mel_minor":    [0, 2, 3, 5, 7, 9, 11],

    # 2 octave
    'pentatonic2': [0, 3, 5, 7, 10, 12, 15, 17, 19, 22],
}

spectral_bands = {
    'slow': [0,2],
    'delta': [2,4],
    'theta': [4,8],
    'alpha': [8,12],
    'beta1': [12,20],
    'beta2': [20,30],
    'gamma': [30,np.inf]
}

if __name__ == "__main__":
    print(scales)