"""Tests for the NP703 model. Run from prakriti_project:   python src/test_nadi.py
Needs models/nadi_model.joblib (run src/train_nadi.py first)."""
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nadi_features import CHANNELS, N_SAMPLES, record_features  # noqa: E402
from train_nadi import MODEL_PATH, load  # noqa: E402

df = load()
key = df[CHANNELS].apply(lambda r: "|".join(",".join(map(str, v)) for v in r), axis=1)
df = df[~key.duplicated()].reset_index(drop=True)          # unique recordings only
X = np.vstack([record_features(r.Vata, r.Pitta, r.Kapha) for r in df.itertuples()])
y = df["prakruti"].to_numpy()
print(f"Unique recordings: {len(df)}\n")

# ---- TEST 1: hold-out test. The test rows are never used for training. ----
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
model = RandomForestClassifier(n_estimators=200, min_samples_leaf=3, random_state=0, n_jobs=-1).fit(Xtr, ytr)
pred = model.predict(Xte)
acc = float((pred == yte).mean())
base = float((DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte) == yte).mean())
k, n = int((pred == yte).sum()), len(yte)
ci = binomtest(k, n).proportion_ci(confidence_level=0.95)
p = binomtest(k, n, p=1 / 3, alternative="greater").pvalue
print("TEST 1: hold-out (20% of recordings, used only once)")
print(f"  test recordings: {n}   correct: {k}   accuracy: {acc:.3f}   (95% CI {ci.low:.2f} to {ci.high:.2f})")
print(f"  always-guess-biggest-class baseline: {base:.3f}   |   guessing at random: 0.333")
print(f"  chance that a random guesser does at least this well: p = {p:.3f}")
labels = sorted(set(y))
print("  confusion matrix (rows = true, columns = predicted):")
print(pd.DataFrame(confusion_matrix(yte, pred, labels=labels), index=labels, columns=labels).to_string())
print(classification_report(yte, pred, zero_division=0))

# ---- TEST 2: the saved model file loads and behaves sensibly. ----
if not MODEL_PATH.exists():
    sys.exit("TEST 2 skipped: run python src/train_nadi.py first.")
bundle = joblib.load(MODEL_PATH)
saved = bundle["pipeline"]
print("TEST 2: saved model file")
assert list(saved.classes_) == labels, "class labels differ"
assert len(bundle["features"]) == X.shape[1] == saved.n_features_in_, "feature count mismatch"
proba = saved.predict_proba(X[:20])
assert np.allclose(proba.sum(axis=1), 1.0), "probabilities do not add up to 1"
assert (saved.predict(X[:20]) == saved.predict(X[:20])).all(), "predictions are not repeatable"
print(f"  OK: classes {list(saved.classes_)}, {saved.n_features_in_} features, probabilities sum to 1, repeatable")

# ---- TEST 3: one made-up recording runs end to end. ----
rng = np.random.default_rng(0)
fake = [505 + rng.normal(0, s, N_SAMPLES) for s in (0.5, 1.2, 0.3)]
out = saved.predict_proba(record_features(*fake).reshape(1, -1))[0]
print("TEST 3: synthetic noise recording ->", {c: round(float(v), 3) for c, v in zip(saved.classes_, out)})
print("  (the model always names a class, even for noise: it has no 'cannot tell' option)")

# ---- TEST 4: why you must NOT score the saved model on the dataset rows. ----
tr_acc = float((saved.predict(X) == y).mean())
print(f"\nTEST 4: saved model scored on the SAME rows it was trained on: {tr_acc:.3f}")
print("  This number is meaningless (the forest memorised them). Report the hold-out and cross-validation scores instead.")