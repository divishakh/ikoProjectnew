from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import init_db
from .routes import analysis, ayurgenomics, history
from .routes import auth as auth_routes
from .services import inference


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="PRAKRITI AI", lifespan=lifespan)
app.include_router(auth_routes.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(ayurgenomics.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "model": inference.model_status()}