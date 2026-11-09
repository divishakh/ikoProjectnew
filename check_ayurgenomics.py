"""Run from prakriti_project:  python check_ayurgenomics.py
Validates backend/app/data/ayurgenomics.json (every statement has a known source and kind)."""
import importlib.util, sys
from pathlib import Path
root = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ayg", root / "backend/app/services/ayurgenomics.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for p in m.available():
    r = m.profile(p)
    print(p, "OK:", sum(len(s["items"]) for s in r["sections"]), "statements,", len(r["sources"]), "sources")
