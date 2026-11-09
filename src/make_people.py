import numpy as np
import pandas as pd
from synth import synth_pulse
from features import recording_to_features, FEATURE_NAMES

# Three fake body types (test inputs, not real Ayurvedic types)
types = {
    "A": dict(amp=1.5, crest=0.09, width=0.8, jitter=0.01),   # strong, sharp
    "B": dict(amp=0.8, crest=0.18, width=1.4, jitter=0.01),   # weak, slow, broad
    "C": dict(amp=1.0, crest=0.12, width=1.0, jitter=0.08),   # medium, irregular
}

rng = np.random.default_rng(1)
frames = []

for label, p in types.items():
    for i in range(6):
        person_id = f"{label}{i}"
        _, x = synth_pulse(
            hr=rng.uniform(62, 85),
            seed=int(rng.integers(1_000_000)),
            amp=p["amp"] * rng.uniform(0.85, 1.15),
            crest=p["crest"] * rng.uniform(0.9, 1.1),
            width=p["width"],
            jitter=p["jitter"],
        )
        f = pd.DataFrame(recording_to_features(x), columns=FEATURE_NAMES)
        f["person"] = person_id
        f["label"] = label
        frames.append(f)

df = pd.concat(frames, ignore_index=True)
df.to_csv("data/synthetic/features.csv", index=False)

print("total rows (beats):", len(df))
print()
print("beats kept per person:")
print(df.groupby("person").size().to_string())
print()
print("average features per type:")
print(df.groupby("label")[FEATURE_NAMES].mean().round(3))
