"""Request/response models for the API."""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LineItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    qty: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal | None = None
    predicted_gl_account_id: int | None = None
    gl_confidence: float | None = None


class ExtractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stage_used: str
    vendor_text: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal | None = None
    currency: str | None = None
    line_items: list[LineItemOut] = []


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    message_id: str | None = None
    file_path: str
    doc_type: str | None = None
    status: str
    confidence: float | None = None
    created_at: datetime | None = None


class DocumentDetailOut(DocumentOut):
    extraction: ExtractionOut | None = None
    # match verdict + confidence breakdown get attached here by the
    # judgment layer in Week 2 (three-way match, Day 12; confidence, Day 13-14).


class CorrectionIn(BaseModel):
    """One field correction from the review queue.

    Stored as a review_actions row (field, old_value, new_value) — the
    extraction itself is never edited in place.
    """

    field: str
    old_value: str | None = None
    new_value: str


class BenchmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_date: datetime | None = None
    benchmark_size: int
    field_accuracy_json: dict | None = None
    auto_post_rate: float | None = None
    notes: str | None = None
