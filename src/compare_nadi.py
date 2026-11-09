"""Compare Random Forest, SVM and Multilayer Perceptron (MLP) on data/nadi/dataset.csv.

Run from the prakriti_project folder:   python src/compare_nadi.py
Writes: models/nadi_comparison.json  (and models/nadi_svm.joblib, models/nadi_mlp.joblib)

It reuses load() from train_nadi.py and record_features() from nadi_features.py,
so the data, duplicate removal and the 57 features are exactly the same as for
the Random Forest. All models are scored on the SAME cross-validation folds.
"""
import json
import sys
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import (GridSearchCV, RepeatedStratifiedKFold,
                                     StratifiedKFold, cross_val_predict,
                                     cross_val_score, permutation_test_score)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nadi_features import CHANNELS, feature_names, record_features  # noqa: E402
from train_nadi import ROOT, SEED, load  # noqa: E402

warnings.filterwarnings("ignore")

N_PERMUTATIONS = 20      # raise to 60-100 for the final report (slower)


def get_data():
    df = load()
    key = df[CHANNELS].apply(lambda r: "|".join(",".join(map(str, v)) for v in r), axis=1)
    df = df[~key.duplicated()].reset_index(drop=True)          # unique recordings only
    X = np.vstack([record_features(r.Vata, r.Pitta, r.Kapha) for r in df.itertuples()])
    # MLP early-stopping breaks on text labels, so use numbers 0/1/2 (Kapha/Pitta/Vata)
    le = LabelEncoder()
    y = le.fit_transform(df["prakruti"].to_numpy())
    return X, y, le


def make_models():
    inner = StratifiedKFold(3, shuffle=True, random_state=SEED)   # tuning folds (inside each outer fold)

    rf = RandomForestClassifier(n_estimators=200, min_samples_leaf=3,
                                random_state=SEED, n_jobs=-1)

    # SVM and MLP are sensitive to feature scale -> StandardScaler first.
    svm = GridSearchCV(
        Pipeline([("scale", StandardScaler()), ("clf", SVC(kernel="rbf", probability=True, random_state=SEED))]),
        {"clf__C": [0.1, 1, 10, 100], "clf__gamma": ["scale", 0.01, 0.001]},
        cv=inner, scoring="accuracy", n_jobs=-1)

    mlp = GridSearchCV(
        Pipeline([("scale", StandardScaler()),
                  ("clf", MLPClassifier(max_iter=1000, early_stopping=True, random_state=SEED))]),
        {"clf__hidden_layer_sizes": [(32,), (64, 32)],
         "clf__alpha": [1e-3, 1e-1],
         "clf__learning_rate_init": [1e-3, 1e-2]},
        cv=inner, scoring="accuracy", n_jobs=-1)

    return {"Random Forest": rf, "SVM (RBF)": svm, "MLP": mlp}


def main():
    t0 = time.time()
    X, y, le = get_data()
    classes = list(range(len(le.classes_)))
    names = list(le.classes_)
    counts = pd.Series(le.inverse_transform(y)).value_counts()
    print(f"Unique recordings: {len(y)} | features: {X.shape[1]} | classes: {counts.to_dict()}")

    rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=SEED)   # same folds for all models
    cv5 = StratifiedKFold(5, shuffle=True, random_state=SEED)
    base = cross_val_score(DummyClassifier(strategy="most_frequent"), X, y, cv=rcv).mean()

    results = {}
    for name, model in make_models().items():
        print(f"\n=== {name} ===")
        scores = cross_val_score(model, X, y, cv=rcv)
        pred = cross_val_predict(model, X, y, cv=cv5)
        cm = confusion_matrix(y, pred, labels=classes)
        _, _, p = permutation_test_score(model, X, y, cv=cv5, n_permutations=N_PERMUTATIONS,
                                         random_state=SEED, n_jobs=1)
        print(f"CV accuracy: {scores.mean():.3f} +/- {scores.std():.3f}   (baseline {base:.3f})")
        print(pd.DataFrame(cm, index=names, columns=names).to_string())
        print(f"Permutation p-value: {p:.3f} ->",
              "better than chance" if p < 0.05 and scores.mean() > base else "NOT better than chance")
        results[name] = {"cv_accuracy_mean": round(float(scores.mean()), 3),
                         "cv_accuracy_std": round(float(scores.std()), 3),
                         "permutation_p_value": round(float(p), 3),
                         "confusion_matrix": cm.tolist()}

    print("\n" + "=" * 52)
    print(f"{'Model':<16}{'Accuracy':>10}{'Std':>8}{'p-value':>10}")
    for n, r in results.items():
        print(f"{n:<16}{r['cv_accuracy_mean']:>10.3f}{r['cv_accuracy_std']:>8.3f}{r['permutation_p_value']:>10.3f}")
    print(f"{'Baseline':<16}{base:>10.3f}")

    # Save SVM and MLP trained on all unique recordings (same bundle layout as nadi_model.joblib)
    models = make_models()
    for name, fname in [("SVM (RBF)", "nadi_svm.joblib"), ("MLP", "nadi_mlp.joblib")]:
        m = models[name].fit(X, y)
        joblib.dump({"pipeline": m.best_estimator_, "features": feature_names(),
                     "classes": names,
                     "info": {"name": f"NP703 {name}", "best_params": m.best_params_,
                              **results[name], "validated": False}},
                    ROOT / "models" / fname)
    (ROOT / "models" / "nadi_comparison.json").write_text(
        json.dumps({"baseline": round(float(base), 3), "models": results}, indent=2))
    print(f"\nSaved models/nadi_svm.joblib, models/nadi_mlp.joblib, models/nadi_comparison.json")
    print(f"Finished in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
