"""Literature knowledge base for the Ayurgenomics panel.

Everything shown comes from backend/app/data/ayurgenomics.json, where each statement carries its sources
(S1-S5) and a 'kind' (study / classical / hypothesis / note). Nothing here is computed from the person's data.
"""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "ayurgenomics.json"
KINDS = {"study", "classical", "hypothesis", "note"}
_cache: dict = {}


class UnknownPrakriti(KeyError):
    pass


def _load() -> dict:
    if not _cache:
        kb = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        validate(kb)
        _cache.update(kb)
    return _cache


def validate(kb: dict) -> None:
    """Fail loudly if the data file has a bad source id or kind (run by tests and on first load)."""
    ids = set(kb["sources"])
    def check(entry, where):
        if entry["kind"] not in KINDS:
            raise ValueError(f"{where}: bad kind {entry['kind']!r}")
        bad = [s for s in entry["sources"] if s not in ids]
        if bad:
            raise ValueError(f"{where}: unknown source {bad}")
    for c in kb["concepts"]:
        check(c, "concept " + c["title"])
    for name, p in kb["prakriti"].items():
        for sec in p["sections"]:
            for i, item in enumerate(sec["items"]):
                check(item, f"{name}/{sec['id']}[{i}]")


def available() -> list:
    return list(_load()["prakriti"])


def profile(prakriti: str) -> dict:
    kb = _load()
    key = next((k for k in kb["prakriti"] if k.lower() == (prakriti or "").strip().lower()), None)
    if key is None:
        raise UnknownPrakriti(prakriti)
    rasa = {taste: {"effect": ("increases" if key in v["increases"] else "pacifies" if key in v["pacifies"] else "neutral")}
            for taste, v in kb["rasa"].items()}
    used = {s for sec in kb["prakriti"][key]["sections"] for it in sec["items"] for s in it["sources"]}
    used |= {s for c in kb["concepts"] for s in c["sources"]} | {"S5"}
    return {
        "prakriti": key,
        "available": list(kb["prakriti"]),
        "summary": kb["prakriti"][key]["summary"],
        "sections": kb["prakriti"][key]["sections"],
        "tastes": {"note": kb["rasa_note"], "items": rasa},
        "concepts": kb["concepts"],
        "caveats": kb["caveats"],
        "sources": {k: v for k, v in kb["sources"].items() if k in used},
    }
