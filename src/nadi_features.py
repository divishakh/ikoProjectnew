"""Feature extraction for the NP703-style data: three channels (Vata, Pitta, Kapha),
each a short window of samples. Used by training now and by the website later."""
import numpy as np
from scipy.stats import kurtosis, skew

CHANNELS = ["Vata", "Pitta", "Kapha"]
N_SAMPLES = 40          # samples per channel in dataset.csv
N_BINS = 11             # frequency bins kept (1 .. 11 cycles per window)

STAT_NAMES = ["std", "ptp", "mean_abs_diff", "std_diff", "skew", "kurtosis", "first_to_last", "peak_above_mean"]


def channel_features(x):
    """Features of one channel window. The DC offset (mean) is deliberately NOT used,
    because it reflects the sensor's baseline rather than the pulse."""
    x = np.asarray(x, dtype=float)
    xc = x - x.mean()
    d = np.diff(x)
    stats = [
        x.std(), np.ptp(x), np.abs(d).mean(), d.std(),
        skew(x), kurtosis(x), x[-1] - x[0], x.max() - x.mean(),
    ]
    spec = np.abs(np.fft.rfft(xc))[1:N_BINS + 1]
    return np.concatenate([stats, spec])


def feature_names():
    names = []
    for ch in CHANNELS:
        names += [f"{ch}_{s}" for s in STAT_NAMES]
        names += [f"{ch}_fft{i}" for i in range(1, N_BINS + 1)]
    return names


def record_features(vata, pitta, kapha):
    """One recording -> one feature vector (length 3 * (8 + 11) = 57)."""
    return np.concatenate([channel_features(vata), channel_features(pitta), channel_features(kapha)])