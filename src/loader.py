import numpy as np
import pandas as pd

def load_recording(path):
    """Read a standard-format CSV. Returns (dataframe, sampling rate in Hz)."""
    df = pd.read_csv(path)
    fs = float(round(1 / np.median(np.diff(df["time_s"].values))))
    return df, fs