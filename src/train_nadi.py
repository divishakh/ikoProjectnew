"""Train and honestly evaluate a Prakriti classifier on data/nadi/dataset.csv.

Run from the prakriti_project folder:   python src/train_nadi.py
Writes: models/nadi_model.joblib  and  models/nadi_report.json
"""
import json
import re
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import (RepeatedStratifiedKFold, StratifiedKFold,
                                     cross_val_predict, cross_val_score,
                                     permutation_test_score)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nadi_features import CHANNELS, feature_names, record_features  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "nadi" / "dataset.csv"
MODEL_PATH = ROOT / "models" / "nadi_model.joblib"
REPORT_PATH = ROOT / "models" / "nadi_report.json"
SEED = 0


def parse(cell):
    """Handles both '[1.0, 2.0]' and numpy-style '[1.0 2.0]' cells."""
    return np.array([float(v) for v in re.split(r"[,\s]+", str(cell).strip().strip("[]")) if v])


def load():
    if not DATA.exists():
        sys.exit(f"Dataset not found: {DATA}\nCopy dataset.csv into data\\nadi\\ first.")
    df = pd.read_csv(DATA)
    need = CHANNELS + ["prakruti"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        sys.exit(f"Missing columns in the CSV: {missing}")
    for c in CHANNELS:
        df[c] = df[c].apply(parse)
    ok = df[CHANNELS].apply(lambda col: col.apply(len) == 40).all(axis=1)
    if not ok.all():
        print(f"Dropping {(~ok).sum()} rows whose channels are not 40 samples long.")
        df = df[ok]
    return df.reset_index(drop=True)


def main():
    t0 = time.time()
    df = load()
    print(f"Rows in file: {len(df)}")

    # 1. Remove exact duplicate recordings (same three signals). Keeping them would let the
    #    same recording appear in both the training and the test folds and inflate accuracy.
    key = df[CHANNELS].apply(lambda r: "|".join(",".join(map(str, v)) for v in r), axis=1)
    n_dupes = int(key.duplicated().sum())
    df = df[~key.duplicated()].reset_index(drop=True)
    print(f"Exact duplicate rows removed: {n_dupes}  ->  unique recordings: {len(df)}")
    counts = df["prakruti"].value_counts()
    print("Class counts:", counts.to_dict())

    X = np.vstack([record_features(r.Vata, r.Pitta, r.Kapha) for r in df.itertuples()])
    y = df["prakruti"].to_numpy()
    classes = sorted(set(y))
    chance = counts.max() / len(df)
    print(f"Features per recording: {X.shape[1]}   |   always-guess-the-biggest-class accuracy: {chance:.3f}")

    def make_model():
        return RandomForestClassifier(n_estimators=200, min_samples_leaf=3, random_state=SEED, n_jobs=-1)

    # 2. Honest evaluation: 5 x repeated 5-fold cross-validation on UNIQUE recordings.
    rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)
    scores = cross_val_score(make_model(), X, y, cv=rcv)
    base = cross_val_score(DummyClassifier(strategy="most_frequent"), X, y, cv=rcv)
    print(f"\nModel accuracy (5x5 CV):  {scores.mean():.3f}  +/- {scores.std():.3f}")
    print(f"Baseline (guess biggest class): {base.mean():.3f}")

    # 3. Permutation test: how often does the same model reach this score on SHUFFLED labels?
    print("Running permutation test (1-3 minutes)...")
    cv5 = StratifiedKFold(5, shuffle=True, random_state=SEED)
    perm_score, perm_scores, p_value = permutation_test_score(
        make_model(), X, y, cv=cv5, n_permutations=60, random_state=SEED, n_jobs=1)
    print(f"Permutation test: score {perm_score:.3f}, shuffled-label mean {perm_scores.mean():.3f}, p = {p_value:.3f}")

    # 4. Where does it go right and wrong?
    pred = cross_val_predict(make_model(), X, y, cv=cv5)
    cm = confusion_matrix(y, pred, labels=classes)
    print("\nConfusion matrix (rows = true, columns = predicted):")
    print(pd.DataFrame(cm, index=classes, columns=classes).to_string())

    # 5. Final model on all unique recordings.
    model = make_model().fit(X, y)
    imp = sorted(zip(feature_names(), model.feature_importances_), key=lambda t: -t[1])[:8]
    print("\nMost used features (global importance, not proof of a real effect):")
    for n, v in imp:
        print(f"  {n:24s} {v:.3f}")

    significant = bool(p_value < 0.05 and scores.mean() > base.mean())
    info = {
        "name": "NP703 Random Forest (demonstration)",
        "dataset": "NP703 dataset.csv",
        "rows_in_file": int(len(df) + n_dupes),
        "duplicate_rows_removed": n_dupes,
        "unique_recordings": int(len(df)),
        "classes": classes,
        "n_features": int(X.shape[1]),
        "cv_accuracy_mean": round(float(scores.mean()), 3),
        "cv_accuracy_std": round(float(scores.std()), 3),
        "baseline_accuracy": round(float(base.mean()), 3),
        "permutation_p_value": round(float(p_value), 3),
        "better_than_chance": significant,
        "validated": False,
        "note": "Window length 40 samples, sampling rate unknown. Not clinically validated.",
    }
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"pipeline": model, "features": feature_names(), "info": info}, MODEL_PATH)
    REPORT_PATH.write_text(json.dumps({**info, "confusion_matrix": cm.tolist(),
                                       "top_features": [[n, round(float(v), 4)] for n, v in imp]}, indent=2))
    print(f"\nSaved: {MODEL_PATH}\nSaved: {REPORT_PATH}")
    print("\nVERDICT:", "better than chance (p < 0.05)." if significant else
          "NOT distinguishable from chance. Do not present predictions from this model as real.")
    print(f"Finished in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()