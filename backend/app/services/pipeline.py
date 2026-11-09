"""Runs the project's real signal-processing code (src/clean.py, src/features.py) on a recording."""
import inspect
import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]            # the prakriti_project folder
sys.path.insert(0, str(ROOT / "src"))
from clean import PRE, bandpass, cut_beats, quality_gate    # noqa: E402
from features import FEATURE_NAMES, beat_features           # noqa: E402

MIN_SECONDS = 10          # shortest recording accepted
MAX_SECONDS = 300         # longest recording accepted (keeps processing fast)
MIN_GOOD_BEATS = 40       # same rule as src/check_session.py
MIN_KEPT_FRACTION = 0.7
PLOT_SECONDS = 10         # seconds of signal sent to the charts


class PulseError(ValueError):
    """A problem with the uploaded recording that the user can fix."""


def read_csv_bytes(data: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(io.BytesIO(data))
    except Exception:
        raise PulseError("The file could not be read as a CSV.")


def filter_settings() -> dict:
    p = inspect.signature(bandpass).parameters      # read the real defaults from clean.py
    return {"type": "Butterworth band-pass", "order": 3, "low_hz": p["lo"].default,
            "high_hz": p["hi"].default, "zero_phase": True, "method": "scipy filtfilt"}


def analyze(df: pd.DataFrame, channel: str = "ch1"):
    """Returns (result dict for the website, per-beat feature array for the model)."""
    if "time_s" not in df.columns or channel not in df.columns:
        raise PulseError(f"The CSV needs the columns time_s and {channel}.")
    t = pd.to_numeric(df["time_s"], errors="coerce").to_numpy(float)
    x = pd.to_numeric(df[channel], errors="coerce").to_numpy(float)
    keep = np.isfinite(t) & np.isfinite(x)
    if keep.sum() < 0.9 * len(t):
        raise PulseError("More than 10% of the rows contain missing or non-numeric values.")
    t, x = t[keep], x[keep]
    if len(t) < 3 or np.any(np.diff(t) <= 0):
        raise PulseError("time_s must increase from row to row.")
    fs = float(round(1 / np.median(np.diff(t))))
    if not 50 <= fs <= 1000:
        raise PulseError(f"Sampling rate {fs:.0f} Hz is outside the supported range of 50 to 1000 Hz.")
    duration = float(t[-1] - t[0])
    if duration < MIN_SECONDS:
        raise PulseError(f"The recording is {duration:.1f} s long. At least {MIN_SECONDS} s is needed.")
    if duration > MAX_SECONDS:
        raise PulseError(f"The recording is {duration:.0f} s long. The maximum is {MAX_SECONDS} s.")
    if np.std(x) < 1e-9:
        raise PulseError("The signal is flat (no variation).")

    xf = bandpass(x, fs)
    peaks, beats = cut_beats(xf, fs)
    if len(beats) < 3:
        raise PulseError("No clear heartbeats were found. Check the sensor contact and the signal.")
    good = quality_gate(beats)
    kept = int(good.sum())
    frac = kept / len(beats)
    t0 = t[0]
    n = int(PLOT_SECONDS * fs)
    result = {
        "recording": {"channel": channel, "sampling_hz": fs, "duration_s": round(duration, 1), "samples": int(len(x))},
        "filter": filter_settings(),
        "quality": {"beats_found": len(beats), "beats_kept": kept, "kept_fraction": round(frac, 3),
                    "ok": bool(kept >= MIN_GOOD_BEATS and frac >= MIN_KEPT_FRACTION),
                    "rule": f"at least {MIN_GOOD_BEATS} kept beats and at least {int(MIN_KEPT_FRACTION * 100)}% kept"},
        "signal": {"t": [round(float(v - t0), 3) for v in t[:n]],
                   "raw": [round(float(v), 4) for v in x[:n]],
                   "filtered": [round(float(v), 4) for v in xf[:n]],
                   "peaks_t": [round(float(t[p] - t0), 3) for p in peaks if p < n]},
        "beat_intervals_s": [round(float(v), 3) for v in np.diff(peaks) / fs],
    }
    feats = None
    if kept >= 2:
        feats = beat_features(beats[good], peaks, fs)
        med = np.median(beats[good], axis=0)
        result["features"] = dict(zip(FEATURE_NAMES, [round(float(v), 4) for v in feats.mean(axis=0)]))
        result["median_beat"] = {"t": [round(float(i / fs - PRE), 3) for i in range(len(med))],
                                 "y": [round(float(v), 4) for v in med]}
    return result, feats