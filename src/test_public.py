import numpy as np
import time
import pandas as pd
import wfdb
import matplotlib.pyplot as plt
from clean import bandpass, cut_beats, quality_gate, PRE
from features import beat_features

PN = "bidmc/1.0.0"     # PhysioNet folder
MIN_CORR = 0.9         # quality threshold; try 0.8 if too many beats are rejected
SECONDS = 60           # use the first minute of each recording
CACHE = {}

def read_rec(name, tries=4):
    """Download a record once, retrying if the connection drops."""
    if name in CACHE:
        return CACHE[name]
    for attempt in range(1, tries + 1):
        try:
            rec = wfdb.rdrecord(name, pn_dir=PN)
            CACHE[name] = rec
            return rec
        except Exception as e:
            print(f"  {name}: attempt {attempt} failed ({type(e).__name__}), retrying...", flush=True)
            time.sleep(2)
    raise RuntimeError(f"could not download {name}")
def find_channel(names, key):
    """Signal names in this dataset have trailing commas, e.g. 'PLETH,'."""
    for i, n in enumerate(names):
        if n.strip().strip(",").upper() == key:
            return i
    raise ValueError(f"channel {key} not found in {names}")

def load_ppg(name):
    rec = read_rec(name)
    i = find_channel(rec.sig_name, "PLETH")
    fs = int(rec.fs)
    return rec.p_signal[:fs * SECONDS, i], fs

def monitor_hr(name):
    """Heart rate from the hospital monitor (numerics file), for comparison."""
    try:
        rec = read_rec(name + "n")
        i = find_channel(rec.sig_name, "HR")
        return round(float(np.nanmean(rec.p_signal[:SECONDS, i])), 1)
    except Exception:
        return float("nan")

# ---- Table for the first 10 recordings ----
rows = []
for n in range(1, 4):
    name = f"bidmc{n:02d}"
    print("loading", name, flush=True)
    try:
        x, fs = load_ppg(name)
        xf = bandpass(x, fs)
        peaks, beats = cut_beats(xf, fs)
        good = quality_gate(beats, MIN_CORR)
        feats = beat_features(beats[good], peaks, fs)
        rows.append(dict(recording=name, fs=fs, found=len(beats),
                         kept=int(good.sum()),
                         hr_ours=round(float(feats[:, 4].mean()), 1),
                         hr_monitor=monitor_hr(name)))
    except Exception as e:
        print(name, "failed:", e)

print(pd.DataFrame(rows).to_string(index=False))

# ---- Plots and standard-format CSV for recording 1 ----
x, fs = load_ppg("bidmc01")
xf = bandpass(x, fs)
peaks, beats = cut_beats(xf, fs)
good = quality_gate(beats, MIN_CORR)
t = np.arange(len(x)) / fs
n10 = fs * 10

fig, ax = plt.subplots(3, 1, figsize=(10, 9))
ax[0].plot(t[:n10], x[:n10])
ax[0].set_title("Raw pulse (first 10 s)")
ax[1].plot(t[:n10], xf[:n10], color="green")
pk = peaks[peaks < n10]
ax[1].plot(pk / fs, xf[pk], "ro")
ax[1].set_title("Filtered, with detected peaks")
tb = np.arange(beats.shape[1]) / fs - PRE
for b in beats[good]:
    ax[2].plot(tb, b, color="green", alpha=0.2)
for b in beats[~good]:
    ax[2].plot(tb, b, color="red", alpha=0.6)
ax[2].set_title("Kept beats (green) and rejected beats (red)")
ax[2].set_xlabel("seconds from peak")
plt.tight_layout()
plt.savefig("results/public_check.png")
plt.show()

pd.DataFrame({"time_s": t, "ch1": x, "ch2": np.nan, "ch3": np.nan,
              "temp_C": np.nan, "humidity_pct": np.nan}
             ).to_csv("data/public/bidmc01.csv", index=False)
print("saved data/public/bidmc01.csv (125 Hz, standard columns)")