"""Benchmark reporting — the numbers that make this project senior.

Field-level accuracy (vendor, invoice number, total, dates, line items kept
separate — a blended number hides the truth) plus the auto-post rate at the
calibrated threshold. Runs are produced by the Week 2/3 benchmark work and
stored in eval_runs; this endpoint serves the latest one.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import EvalRun
from ..schemas import BenchmarkOut

router = APIRouter(tags=["benchmark"])


@router.get("/benchmark", response_model=BenchmarkOut | None)
def latest_benchmark(db: Session = Depends(get_db)):
    return db.query(EvalRun).order_by(EvalRun.run_date.desc()).first()
