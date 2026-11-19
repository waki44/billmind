"""BillMind API — entry point.

Run: uvicorn app.main:app --reload   (docs at /docs)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import init_db
from .routers import benchmark, documents, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Day-1 convenience: make sure the tables exist (SQLite local dev).
    # Postgres under Docker Compose uses the same models.
    init_db()
    yield


app = FastAPI(
    title="BillMind",
    description="AP inbox → coded, PO-matched, reconciled bills.",
    lifespan=lifespan,
)
app.include_router(documents.router)
app.include_router(ingest.router)
app.include_router(benchmark.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "billmind"}
