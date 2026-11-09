import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier

FEATURES = ["amp", "rise_s", "width_s", "irregularity", "hr"]

df = pd.read_csv("data/synthetic/features.csv")
X = df[FEATURES].values
y = df["label"].values
g = df["person"].values

models = {
    "dummy":    DummyClassifier(strategy="uniform", random_state=0),
    "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "forest":   RandomForestClassifier(n_estimators=200, random_state=0),
}

rng = np.random.default_rng(0)

def person_level_accuracy(model, X, y, g):
    """Hold out one person at a time, then give each person one vote (majority of their beats)."""
    pred = cross_val_predict(model, X, y, groups=g, cv=LeaveOneGroupOut())
    d = pd.DataFrame({"person": g, "true": y, "pred": pred})
    per = d.groupby("person").agg(true=("true", "first"),
                                  pred=("pred", lambda s: s.mode()[0]))
    ok = (per["true"] == per["pred"]).values
    boots = [rng.choice(ok, len(ok)).mean() for _ in range(2000)]
    return ok.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5), per

print("=== Real labels ===")
for name, m in models.items():
    acc, lo, hi, per = person_level_accuracy(m, X, y, g)
    print(f"{name:9s} accuracy {acc:.2f}   95% CI {lo:.2f}-{hi:.2f}")

# Sanity check: shuffle labels between PEOPLE (not beats). Accuracy should fall to chance.
persons = df.groupby("person")["label"].first()
shuffled = dict(zip(persons.index, rng.permutation(persons.values)))
y_shuf = df["person"].map(shuffled).values

print()
print("=== Shuffled labels (should be near 0.33) ===")
acc, lo, hi, _ = person_level_accuracy(models["forest"], X, y_shuf, g)
print(f"forest    accuracy {acc:.2f}   95% CI {lo:.2f}-{hi:.2f}")

# Which people were wrong? (forest, real labels)
acc, lo, hi, per = person_level_accuracy(models["forest"], X, y, g)
print()
print("Confusion table (rows = true, columns = predicted):")
print(pd.crosstab(per["true"], per["pred"]))