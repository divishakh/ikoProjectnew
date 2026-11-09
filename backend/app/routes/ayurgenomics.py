from fastapi import APIRouter, HTTPException

from ..services import ayurgenomics

router = APIRouter(prefix="/api/ayurgenomics", tags=["ayurgenomics"])


@router.get("")
def list_prakriti():
    return {"prakriti": ayurgenomics.available()}


@router.get("/{prakriti}")
def get_profile(prakriti: str):
    try:
        return ayurgenomics.profile(prakriti)
    except ayurgenomics.UnknownPrakriti:
        raise HTTPException(404, f"No literature profile for '{prakriti}'. Available: "
                                 + ", ".join(ayurgenomics.available()) + ".")
