import numpy as np
from clean import bandpass, cut_beats, quality_gate, PRE

FEATURE_NAMES = ["amp", "rise_s", "width_s", "irregularity", "hr"]

def beat_features(beats, all_peaks, fs=100):
    ibi = np.diff(all_peaks) / fs             # gaps from ALL detected peaks
    irregularity = np.std(ibi) / np.mean(ibi)
    hr = 60 / np.mean(ibi)
    k = int(PRE * fs)                         # index of the peak inside each beat
    rows = []
    for b in beats:
        foot = np.argmin(b[:k + 1])           # lowest point before the peak
        amp = b[k] - b[foot]                  # strength
        rise = (k - foot) / fs                # time from foot to peak
        half = b[foot] + amp / 2
        above = b > half
        l = k
        while l > 0 and above[l - 1]:
            l -= 1
        r = k
        while r < len(b) - 1 and above[r + 1]:
            r += 1
        width = (r - l + 1) / fs              # width of the MAIN peak only
        rows.append([amp, rise, width, irregularity, hr])
    return np.array(rows)

def recording_to_features(x, fs=100):
    x = bandpass(x, fs)
    peaks, beats = cut_beats(x, fs)
    good = quality_gate(beats)
    return beat_features(beats[good], peaks, fs)   # peaks (all), not peaks[good]