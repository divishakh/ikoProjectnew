import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from clean import bandpass, cut_beats, quality_gate

FS = 100
df = pd.read_csv("data/synthetic/synth_test.csv")
x = bandpass(df["ch1"].values, fs=FS)

peaks, beats = cut_beats(x, fs=FS)
good = quality_gate(beats)

gaps = np.diff(peaks) / FS
print("beats found:       ", len(beats))
print("beats passing gate:", int(good.sum()))
print("average gap (s):   ", round(gaps.mean(), 3))
print("heart rate (bpm):  ", round(60 / gaps.mean(), 1))

# Plot all beats on top of each other
tb = np.arange(beats.shape[1]) / FS - 0.25
fig, ax = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for b in beats[good]:
    ax[0].plot(tb, b, color="green", alpha=0.3)
for b in beats[~good]:
    ax[1].plot(tb, b, color="red", alpha=0.6)
ax[0].set_title("Kept beats")
ax[1].set_title("Rejected beats")
ax[0].set_xlabel("seconds from peak")
ax[1].set_xlabel("seconds from peak")
plt.tight_layout()
plt.savefig("results/beats_check.png")
plt.show()
rng = np.random.default_rng(0)
bad = beats.copy()
bad[::10] += rng.normal(0, 0.5, bad[::10].shape)   # every 10th beat gets heavy noise
print("gate on damaged beats: kept", int(quality_gate(bad).sum()), "of", len(bad))