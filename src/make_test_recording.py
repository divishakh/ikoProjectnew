import numpy as np
import pandas as pd

fs = 100
t = np.arange(0, 60, 1 / fs)          # 60 seconds at 100 samples per second
ph = (t * 1.2) % 1                    # 1.2 beats per second = 72 bpm
beat = lambda p: np.exp(-((p - 0.1) / 0.05) ** 2) + 0.35 * np.exp(-((p - 0.42) / 0.08) ** 2)
rng = np.random.default_rng(0)

df = pd.DataFrame({"time_s": t.round(3)})
for i, a in enumerate([1.0, 0.8, 0.6], 1):
    df[f"ch{i}"] = (500 + a * 30 * beat(ph) + rng.normal(0, 0.8, len(t))).round(3)
df.to_csv("data/real/test_3channel.csv", index=False)
print("saved data/real/test_3channel.csv")