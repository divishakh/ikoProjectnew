import argparse
import csv
import os
import time

HEADER = ["time_s", "ch1", "ch2", "ch3", "temp_C", "humidity_pct"]

def save(rows, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)

def report(rows, bad_lines, out):
    n = len(rows)
    if n < 2:
        print("No usable samples recorded. Check the port and the ESP32 output format.")
        return
    duration = rows[-1][0] - rows[0][0]
    fs = (n - 1) / duration
    print(f"saved {out}")
    print(f"samples: {n}, duration: {duration:.1f} s, sampling rate: {fs:.1f} Hz, bad lines skipped: {bad_lines}")
    if not 95 <= fs <= 105:
        print("WARNING: sampling rate is not close to 100 Hz. Check the ESP32 timing.")

def record(port, seconds, out, baud=115200):
    """ESP32 must print one line per sample: t_ms,ch1,ch2,ch3,temp_C,humidity_pct"""
    import serial
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)                  # the ESP32 often restarts when the port opens
    ser.reset_input_buffer()
    rows, t_first, bad = [], None, 0
    t_end = time.time() + seconds
    while time.time() < t_end:
        parts = ser.readline().decode(errors="ignore").strip().split(",")
        if len(parts) != 6:
            bad += 1
            continue
        try:
            v = [float(p) for p in parts]
        except ValueError:
            bad += 1
            continue
        if t_first is None:
            t_first = v[0]
        rows.append([(v[0] - t_first) / 1000.0] + v[1:])
    ser.close()
    save(rows, out)
    report(rows, bad, out)

def simulate(seconds, out, hr=72, seed=0):
    """Makes a FAKE recording in the same format, to test the software without hardware."""
    from synth import synth_pulse
    t, x = synth_pulse(duration=seconds, hr=hr, seed=seed)
    rows = [[round(float(ti), 3), xi, 0.9 * xi, 0.8 * xi, 27.5, 45.0] for ti, xi in zip(t, x)]
    save(rows, out)
    report(rows, 0, out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--person", required=True, help="e.g. p01")
    ap.add_argument("--session", default="1")
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--port", default="COM3")
    ap.add_argument("--simulate", action="store_true", help="fake data, no hardware needed")
    a = ap.parse_args()
    if a.simulate:
        simulate(a.seconds, f"data/synthetic/sim_{a.person}_s{a.session}.csv")
    else:
        record(a.port, a.seconds, f"data/real/{a.person}_s{a.session}.csv")