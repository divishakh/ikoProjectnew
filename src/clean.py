import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

PRE, POST = 0.25, 0.65   # seconds kept before / after each peak

def bandpass(x, fs=100, lo=0.5, hi=8.0):
    """Remove slow drift (below lo Hz) and fast noise (above hi Hz)."""
    b, a = butter(3, [lo / (fs / 2), hi / (fs / 2)], btype="band")
    return filtfilt(b, a, x)

def fill_missed_peaks(x, peaks, fs=100, low_prom=0.25):
    """Recover a beat the main detector skipped inside an unusually long gap.

    Only gaps longer than 1.5x the median interval are examined. A candidate
    is accepted only if it splits the gap into two intervals that are both
    within 0.6-1.4x the median interval, so a dicrotic notch or noise bump
    is not mistaken for a beat. Recordings without long gaps are unchanged.
    """
    if len(peaks) < 4:
        return peaks
    med = np.median(np.diff(peaks))
    cand, _ = find_peaks(x, distance=int(0.4 * fs), prominence=low_prom * np.std(x))
    cand = np.setdiff1d(cand, peaks)
    added = []
    for a, b in zip(peaks[:-1], peaks[1:]):
        if b - a > 1.5 * med:
            ok = [c for c in cand
                  if a < c < b and 0.6 * med <= c - a <= 1.4 * med and 0.6 * med <= b - c <= 1.4 * med]
            if ok:
                added.append(max(ok, key=lambda c: x[c]))
    if not added:
        return peaks
    return np.array(sorted(list(peaks) + added))

def cut_beats(x, fs=100):
    """Find pulse peaks and cut a fixed window around each one."""
    peaks, _ = find_peaks(x, distance=int(0.4 * fs), prominence=0.5 * np.std(x))
    peaks = fill_missed_peaks(x, peaks, fs)
    before, after = int(PRE * fs), int(POST * fs)
    keep_peaks, beats = [], []
    for p in peaks:
        if p - before >= 0 and p + after <= len(x):   # skip beats cut off at the edges
            beats.append(x[p - before:p + after])
            keep_peaks.append(p)
    return np.array(keep_peaks), np.array(beats)

def quality_gate(beats, min_corr=0.9):
    """True for beats that resemble the typical (median) beat."""
    template = np.median(beats, axis=0)
    return np.array([np.corrcoef(b, template)[0, 1] > min_corr for b in beats])