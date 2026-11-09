# Prakriti pulse project

## Standard data format (all datasets must be converted to this)
CSV file with header: time_s,ch1,ch2,ch3,temp_C,humidity_pct
- Sampling rate: 100 samples per second (stored separately if different)
- time_s: seconds from the start of recording
- ch1, ch2, ch3: pulse signal from the three wrist pads
- temp_C, humidity_pct: room conditions (blank/NaN if not available)

## File naming
- Synthetic: data/synthetic/synth_A0.csv
- Public:    data/public/bidmc01.csv
- Real:      data/real/p01_s1.csv  (person 01, session 1)