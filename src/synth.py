import numpy as np

FS = 100

def synth_pulse(duration=60, hr=72, amp=1.0, crest=0.12, width=1.0,
                jitter=0.0, noise=0.03, seed=0):
    """Make a fake pulse signal. Returns (time array, signal array)."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, duration, 1 / FS)
    x = np.zeros_like(t)

    starts = np.arange(0, duration, 60 / hr)
    starts = starts + rng.normal(0, jitter, len(starts))   # irregular timing

    for s in starts:
        tt = t - s
        x += amp * np.exp(-((tt - crest) ** 2) / (2 * (0.03 * width) ** 2))               # main peak
        x += 0.4 * amp * np.exp(-((tt - crest - 0.18) ** 2) / (2 * (0.05 * width) ** 2))  # reflected bump
        x += 0.15 * amp * np.exp(-((tt - crest - 0.35) ** 2) / (2 * (0.06 * width) ** 2)) # late bump

    x += 0.3 * np.sin(2 * np.pi * 0.25 * t)       # breathing drift
    x += noise * rng.standard_normal(len(t))      # electrical noise
    return t, x