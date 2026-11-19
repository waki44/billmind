"""Day-1 smoke tests: the scaffolding stands up, the schema is complete,
the seed runs, and the intake path works end to end."""
import os
import sys
from pathlib import Path

# Tests run against a throwaway SQLite file, set before app imports.
os.environ["DATABASE_URL"] = "sqlite:///./test_billmind.db"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402

EXPECTED_TABLES = {
    "vendors",
    "gl_accounts",
    "purchase_orders",
    "po_line_items",
    "documents",
    "extractions",
    "extraction_line_items",
    "bills",
    "matches",
    "review_actions",
    "eval_runs",
}


@pytest.fixture(scope="module", autouse=True)
def _db():
    init_db()
    yield
    Path("./test_billmind.db").unlink(missing_ok=True)


def test_schema_has_all_11_roadmap_tables():
    assert set(models.Base.metadata.tables) == EXPECTED_TABLES


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_seed_is_idempotent_and_complete():
    db = SessionLocal()
    try:
        first = seed(db)
        second = seed(db)
        assert first["gl_accounts"] == 8
        assert first["vendors"] == 3
        assert first["purchase_orders_created"] == 3
        assert second["purchase_orders_created"] == 0  # no duplicates on re-run
        assert db.query(models.PurchaseOrder).count() == 3
        assert db.query(models.POLineItem).count() == 4
    finally:
        db.close()


def test_upload_list_and_reject_flow(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    from app.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        r = client.post(
            "/documents/upload",
            files={"file": ("invoice.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        assert r.status_code == 201
        doc = r.json()
        assert doc["source"] == "upload"
        assert doc["status"] == "received"

        r = client.get("/documents")
        assert any(d["id"] == doc["id"] for d in r.json())

        r = client.post(f"/documents/{doc['id']}/reject")
        assert r.status_code == 200
        assert r.json()["status"] == "rejected"


def test_correction_is_logged_not_edited(tmp_path, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        r = client.post(
            "/documents/upload",
            files={"file": ("inv2.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        doc_id = r.json()["id"]
        r = client.post(
            f"/documents/{doc_id}/correct",
            json={"field": "total", "old_value": "1000", "new_value": "1200"},
        )
        assert r.status_code == 201
    db = SessionLocal()
    try:
        actions = db.query(models.ReviewAction).filter_by(document_id=doc_id).all()
        assert len(actions) == 1
        assert actions[0].field == "total"
        assert actions[0].new_value == "1200"
    finally:
        db.close()


def test_benchmark_empty_until_first_run():
    with TestClient(app) as client:
        r = client.get("/benchmark")
    assert r.status_code == 200
    assert r.json() is None  # no invented numbers before a real run
