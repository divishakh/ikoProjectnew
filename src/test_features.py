import pandas as pd
from synth import synth_pulse
from features import recording_to_features, FEATURE_NAMES

# Two fake body types (labelled A and B, not real Ayurvedic types)
_, xa = synth_pulse(amp=1.5, crest=0.09, width=0.8, seed=1)   # strong, sharp
_, xb = synth_pulse(amp=0.8, crest=0.18, width=1.4, seed=2)   # weak, slow, broad

fa = pd.DataFrame(recording_to_features(xa), columns=FEATURE_NAMES)
fb = pd.DataFrame(recording_to_features(xb), columns=FEATURE_NAMES)

print("Type A beats:", len(fa))
print(fa.mean().round(3))
print()
print("Type B beats:", len(fb))
print(fb.mean().round(3))