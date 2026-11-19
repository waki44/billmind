"""Field extraction — the 3-stage fallback chain.

Stage 1 (Week 1, Day 5-7): native PDF text via PyMuPDF.
Stage 2 (Week 1, Day 5-7): Tesseract OCR for scans/photos.
Stage 3 (Week 2, Day 8-9):  vision LLM, only when stages 1-2 yield
                            incomplete fields.

The chain stops at the first stage that yields COMPLETE fields, and every
result is validated against a strict schema before it is stored (extractions
are immutable once written).

Fields: vendor, invoice number, invoice date, due date, currency, subtotal,
tax, total, line items (description, qty, unit price, amount), PO reference.

TODO(WAQAR): the tuning is the work — which fields each stage can be trusted
on, how you detect a 'complete' extraction, and how OCR garbage gets caught
before it poisons the totals. The cross-check subtotal + tax == total is your
cheapest lie detector; use it per stage, not just at the end.
"""

STAGES = ("text", "ocr", "vision")


def extract_fields(file_path: str) -> dict:
    """Return the extracted fields dict for one document file."""
    raise NotImplementedError("Week 1, Day 5-7 (stages 1-2) / Week 2, Day 8-9 (stage 3).")
