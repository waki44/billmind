# BillMind

An accounts-payable inbox that turns supplier invoices into reviewed, coded, reconciled bills.

**Flow:** Gmail inbox → classify each attachment (invoice / PO / remittance / other) → extract fields with a
3-stage fallback chain → predict GL coding from the business's own posting history → three-way match against
purchase orders → confidence score on every document → score ≥ 85%: bill is drafted automatically in
QuickBooks Online (sandbox); score < 85%: it lands in a human review queue with the PDF beside the extracted
fields → every human correction is logged and feeds the accuracy benchmark.

The senior-level core is the judgment layer, not the OCR: which account, does it match the PO, is it a
duplicate, does the total reconcile — and knowing when NOT to trust the machine.

## Status

- **Day 1 (done):** repo setup, Docker Compose (FastAPI + Postgres), the 11-table schema, seed data
  (chart of accounts + sample vendors/POs), API skeleton with all roadmap endpoints.
- **Judgment layer (the builder's own work, by design):** extraction tuning, the confidence-score formula,
  matching rules and the benchmark — see the `TODO(WAQAR)` markers in `backend/app/pipeline/`.

## Hard rules (never break these)

1. **Totals gate:** if `subtotal + tax != total`, a document can **never** auto-post, whatever its score says.
2. **Extractions are immutable:** a human correction creates a `review_actions` row, never an edit in place.
   That one decision gives the audit trail and the eval dataset for free.
3. **Accuracy numbers are measured, never claimed:** the benchmark set is frozen and hand-labelled before
   tuning; the README/CV get real numbers only after a benchmark run.

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
# API: http://localhost:8000/docs   Health: http://localhost:8000/health
# Seed the chart of accounts + sample vendors/POs:
docker compose exec api python -m app.seed
```

## Quick start (local, no Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# SQLite by default for local dev; set DATABASE_URL for Postgres
uvicorn app.main:app --reload
python -m app.seed
pytest
```

## Layout

```
backend/
  app/
    main.py          FastAPI app (health + routers)
    config.py        Settings (DATABASE_URL, AUTO_POST_THRESHOLD=0.85, ...)
    db.py            Engine/session
    models.py        The 11 roadmap tables (SQLAlchemy)
    schemas.py       Request/response models
    seed.py          Chart of accounts + 3 vendors + sample POs
    routers/         documents, ingest (Gmail), benchmark endpoints
    pipeline/        Judgment layer — classify / extract / confidence / matching
                     (stubs with TODO(WAQAR) markers: this is the interview-defensible core)
  tests/             Smoke tests (health, schema, seed, upload)
docker-compose.yml   api + Postgres 16
```

## API (from the roadmap)

| Endpoint | Purpose |
|---|---|
| `POST /ingest/gmail/sync` | Pull new messages + attachments since last sync (Week 1, Day 2–3) |
| `POST /documents/upload` | Manual intake |
| `GET /documents?status=review` | The review queue |
| `GET /documents/{id}` | Document + extraction + match verdict + confidence breakdown |
| `POST /documents/{id}/approve` | Post bill to QBO sandbox, idempotent (Week 3) |
| `POST /documents/{id}/correct` | Save field corrections (logged to `review_actions`) |
| `POST /documents/{id}/reject` | Not an invoice / unusable |
| `GET /benchmark` | Latest eval run: field-level accuracy + auto-post rate |

## Plan (3 weeks, part-time)

- **Week 1 — Pipeline:** Gmail OAuth + sync, upload, classifier, extraction stages 1–2
  (PyMuPDF text → Tesseract OCR) with strict JSON schema; hand-label the benchmark set.
- **Week 2 — Judgment layer:** vision-LLM fallback, GL prediction from posting history,
  three-way match + duplicate detection, composite confidence score calibrated at the 85% threshold.
- **Week 3 — Product surface:** React review queue, QuickBooks Online sandbox posting (CSV export as
  fallback), full benchmark run, demo + deploy.

## NOT in the MVP (v2)

Production QuickBooks/Xero posting and bank-feed reconciliation · payments · multi-company/multi-user
roles · handwritten invoices · languages other than English.
