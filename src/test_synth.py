import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from synth import synth_pulse

t, x = synth_pulse()


plt.plot(t[:500], x[:500])
plt.xlabel("seconds")
plt.ylabel("signal")
plt.title("Fake pulse (first 5 s)")
plt.savefig("results/synth_check.png")
plt.show()


df = pd.DataFrame({"time_s": t, "ch1": x,
                   "ch2": np.nan, "ch3": np.nan,
                   "temp_C": np.nan, "humidity_pct": np.nan})
df.to_csv("data/synthetic/synth_test.csv", index=False)


back = pd.read_csv("data/synthetic/synth_test.csv")
print(back.head())
print("rows:", len(back))