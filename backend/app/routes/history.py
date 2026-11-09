import json

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_user
from ..db import db

router = APIRouter(prefix="/api/analyses", tags=["history"])


def _summary(row) -> dict:
    r = json.loads(row["result_json"])
    return {"id": row["id"], "filename": row["filename"], "created_at": row["created_at"],
            "duration_s": r["recording"]["duration_s"], "beats_kept": r["quality"]["beats_kept"],
            "quality_ok": r["quality"]["ok"], "hr": r.get("features", {}).get("hr"),
            "prediction_mode": r["prediction"]["mode"]}


@router.get("")
def list_analyses(user=Depends(require_user), conn=Depends(db)):
    rows = conn.execute("SELECT id, filename, created_at, result_json FROM analyses "
                        "WHERE user_id = ? ORDER BY id DESC LIMIT 200", (user["id"],)).fetchall()
    return [_summary(r) for r in rows]


@router.get("/{analysis_id}")
def get_analysis(analysis_id: int, user=Depends(require_user), conn=Depends(db)):
    row = conn.execute("SELECT id, result_json FROM analyses WHERE id = ? AND user_id = ?",
                       (analysis_id, user["id"])).fetchone()
    if row is None:
        raise HTTPException(404, "Analysis not found.")
    result = json.loads(row["result_json"])
    result["id"] = row["id"]
    return result


@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: int, user=Depends(require_user), conn=Depends(db)):
    cur = conn.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user["id"]))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(404, "Analysis not found.")
    return {"status": "deleted"}