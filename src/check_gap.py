import sys
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from clean import bandpass, cut_beats, quality_gate
from features import beat_features

def run(path):
    df = pd.read_csv(path)
    t, x = df["time_s"].to_numpy(float), df["ch1"].to_numpy(float)
    fs = float(round(1 / np.median(np.diff(t))))
    xf = bandpass(x, fs)

    old, _ = find_peaks(xf, distance=int(0.4 * fs), prominence=0.5 * np.std(xf))
    old_ibi = np.diff(old) / fs
    peaks, beats = cut_beats(xf, fs)
    new_ibi = np.diff(peaks) / fs
    good = quality_gate(beats)
    feats = beat_features(beats[good], peaks, fs)

    print(f"\n{path}  ({fs:.0f} Hz)")
    print(f"  old detector: {len(old)} peaks, irregularity {np.std(old_ibi)/np.mean(old_ibi):.4f}, longest gap {old_ibi.max():.3f} s")
    print(f"  new detector: {len(peaks)} beats, {int(good.sum())} kept, irregularity {feats[0, 3]:.4f}, longest gap {new_ibi.max():.3f} s")
    print(f"  median interval {np.median(new_ibi):.3f} s, hr {feats[0, 4]:.1f}")
    added = np.setdiff1d(peaks, old)
    for p in added:
        print(f"  beat added at t = {t[0] + p / fs:.2f} s")

for p in sys.argv[1:]:
    run(p)