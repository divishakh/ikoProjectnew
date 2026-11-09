import sys
from loader import load_recording
from clean import bandpass, cut_beats, quality_gate
from features import recording_to_features, FEATURE_NAMES

path = sys.argv[1]
df, fs = load_recording(path)
x = df["ch1"].values

xf = bandpass(x, fs)
peaks, beats = cut_beats(xf, fs)
good = quality_gate(beats)
found, kept = len(beats), int(good.sum())

print(f"file: {path}")
print(f"sampling rate: {fs:.0f} Hz, length: {len(x) / fs:.0f} s")
print(f"beats found: {found}, kept: {kept} ({100 * kept / max(found, 1):.0f}%)")

if kept >= 2:
    feats = recording_to_features(x, fs)
    for name, val in zip(FEATURE_NAMES, feats.mean(axis=0)):
        print(f"  {name:13s} {val:.3f}")

if kept >= 40 and kept / max(found, 1) >= 0.7:
    print("RESULT: OK, keep this recording")
else:
    print("RESULT: POOR QUALITY, re-record this session")