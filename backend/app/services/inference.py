"""Model inference, kept separate from the API routes so it can be tested on its own.

Two models are supported:
  1. models/prakriti_model.joblib  - the real per-beat model (used if it exists).
  2. models/nadi_model.joblib      - the NP703 demonstration model (3 channels x 40-sample windows).
     It is NOT better than chance (see models/nadi_report.json). It is used only when model 1 is absent.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))                    # for nadi_features
MODEL_PATH = ROOT / "models" / "prakriti_model.joblib"
NADI_PATH = ROOT / "models" / "nadi_model.joblib"

NADI_WINDOW = 40            # samples per window the NP703 model was trained on
NADI_MAX_WINDOWS = 300      # cap, keeps requests fast
_state = {"loaded": False, "model": None}
_nadi = {"loaded": False, "model": None}


def get_model():
    if not _state["loaded"]:
        _state["loaded"] = True
        if MODEL_PATH.exists():
            import joblib
            _state["model"] = joblib.load(MODEL_PATH)
    return _state["model"]


def get_nadi_model():
    if not _nadi["loaded"]:
        _nadi["loaded"] = True
        if NADI_PATH.exists():
            import joblib
            _nadi["model"] = joblib.load(NADI_PATH)
    return _nadi["model"]


def model_status() -> dict:
    m, n = get_model(), get_nadi_model()
    if m is not None:
        return {"available": True, "info": m.get("info", {})}
    if n is not None:
        return {"available": True, "demo": True, "info": n.get("info", {})}
    return {"available": False, "message": "No trained model found yet (models/prakriti_model.joblib)."}


def _three_channels(df):
    """Accepts ch1/ch2/ch3 (project standard) or Vata/Pitta/Kapha columns."""
    for names in (("ch1", "ch2", "ch3"), ("Vata", "Pitta", "Kapha")):
        if all(n in df.columns for n in names):
            return [pd.to_numeric(df[n], errors="coerce").to_numpy(float) for n in names]
    return None


def predict_nadi(df):
    """Window-by-window prediction with the NP703 demonstration model."""
    from nadi_features import feature_names, record_features
    m = get_nadi_model()
    chans = _three_channels(df)
    if chans is None:
        return {"mode": "no_prediction",
                "message": "The Prakriti model needs three channels. Add columns ch1, ch2, ch3 "
                           "(Vata, Pitta, Kapha wrist positions) to the CSV."}
    n = min(len(c) for c in chans)
    chans = [c[:n] for c in chans]
    ok = np.all([np.isfinite(c) for c in chans], axis=0)
    v, p, k = (c[ok] for c in chans)
    n_win = min(len(v) // NADI_WINDOW, NADI_MAX_WINDOWS)
    if n_win < 1:
        return {"mode": "no_prediction", "message": f"Need at least {NADI_WINDOW} valid rows in all three channels."}
    if m["features"] != feature_names():
        return {"mode": "no_prediction", "message": "The saved model does not match the feature code. Re-run train_nadi.py."}
    X = np.vstack([record_features(v[i * NADI_WINDOW:(i + 1) * NADI_WINDOW],
                                   p[i * NADI_WINDOW:(i + 1) * NADI_WINDOW],
                                   k[i * NADI_WINDOW:(i + 1) * NADI_WINDOW]) for i in range(n_win)])
    X = np.nan_to_num(X)                                   # flat windows give NaN skew/kurtosis
    pipe = m["pipeline"]
    prob = pipe.predict_proba(X).mean(axis=0)              # average over the recording's windows
    classes = [str(c) for c in pipe.classes_]
    info = m.get("info", {})
    out = {"mode": "trained", "classes": classes,
           "probabilities": [round(float(x), 3) for x in prob],
           "label": classes[int(np.argmax(prob))], "windows_used": int(n_win), "model_info": info}
    if not info.get("better_than_chance", False):
        out["warning"] = ("Demonstration model: on its test data it was not better than chance "
                          f"({info.get('cv_accuracy_mean')} vs {info.get('baseline_accuracy')} baseline). "
                          "Treat this output as arbitrary.")
    return out


def predict(feats, df=None):
    """feats: per-beat feature array from pipeline.analyze(). df: the uploaded recording."""
    m = get_model()
    if m is None:
        if get_nadi_model() is not None and df is not None:
            return predict_nadi(df)
        return {"mode": "no_model",
                "message": "No trained model is available yet, so no Prakriti prediction is made. "
                           "The signal processing and features shown are real."}
    if feats is None:
        return {"mode": "no_prediction", "message": "Too few clean beats to make a prediction."}
    from .pipeline import FEATURE_NAMES
    X = pd.DataFrame(feats, columns=FEATURE_NAMES)[m["features"]].values
    pipe = m["pipeline"]
    p = pipe.predict_proba(X).mean(axis=0)                 # average over the recording's beats
    classes = [str(c) for c in pipe.classes_]
    return {"mode": "trained", "classes": classes,
            "probabilities": [round(float(v), 3) for v in p],
            "label": classes[int(np.argmax(p))], "model_info": m.get("info", {})}
