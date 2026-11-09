import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..auth import current_user
from ..db import db, now_iso
from ..services import ayurgenomics, inference, pipeline

router = APIRouter(prefix="/api/analyze", tags=["analysis"])
MAX_BYTES = 20_000_000


@router.post("/upload")
async def upload(file: UploadFile = File(...), user=Depends(current_user), conn=Depends(db)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file.")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "The file is too large (20 MB maximum).")
    try:
        df = pipeline.read_csv_bytes(data)
        result, feats = pipeline.analyze(df)
    except pipeline.PulseError as e:
        raise HTTPException(422, str(e))
    result["filename"] = file.filename
    result["prediction"] = inference.predict(feats, df)
    result["saved"] = False
    if user is not None:                       # logged-in users get the analysis saved to their history
        cur = conn.execute("INSERT INTO analyses (user_id, filename, created_at, result_json) VALUES (?,?,?,?)",
                           (user["id"], file.filename, now_iso(), json.dumps(result)))
        conn.commit()
        result["id"], result["saved"] = cur.lastrowid, True
    # Attach the literature profile for the detected type (added after the save so history rows stay small).
    pred = result["prediction"]
    if pred.get("mode") == "trained" and pred.get("label"):
        try:
            result["ayurgenomics"] = ayurgenomics.profile(pred["label"])
        except ayurgenomics.UnknownPrakriti:
            result["ayurgenomics"] = None   # label is not Vata/Pitta/Kapha (e.g. a mixed type): no profile yet
    return result