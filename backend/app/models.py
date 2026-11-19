"""The 11 BillMind tables — exactly as specified in the build roadmap (section 4).

Design rule: extractions are immutable. A human correction creates a
review_actions row, never an edit in place — that gives the audit trail and
the eval dataset for free.
"""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GLAccount(Base):
    """The chart of accounts, imported from the accounting system or seeded."""

    __tablename__ = "gl_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    # Lowercased, punctuation-stripped name — the key fuzzy matching runs on.
    normalised_name: Mapped[str] = mapped_column(String(300), index=True)
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    default_gl_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("gl_accounts.id"), nullable=True
    )

    default_gl_account: Mapped[GLAccount | None] = relationship()


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), index=True)
    po_number: Mapped[str] = mapped_column(String(100), index=True)
    order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open")  # open / closed / cancelled

    vendor: Mapped[Vendor] = relationship()
    line_items: Mapped[list["POLineItem"]] = relationship(back_populates="purchase_order")


class POLineItem(Base):
    __tablename__ = "po_line_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    po_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="line_items")


class Document(Base):
    """One attachment that entered the system, whatever it turns out to be."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(20))  # gmail / upload
    message_id: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    file_path: Mapped[str] = mapped_column(String(500))
    # invoice / purchase_order / remittance / other — set by the classifier (Week 1, Day 4)
    doc_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # received / extracted / review / auto_drafted / posted / rejected
    status: Mapped[str] = mapped_column(String(30), default="received", index=True)
    # Composite confidence, 0..1 — set by the judgment layer (Week 2, Day 13-14)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    extraction: Mapped["Extraction | None"] = relationship(back_populates="document", uselist=False)
    bill: Mapped["Bill | None"] = relationship(back_populates="document", uselist=False)


class Extraction(Base):
    """Immutable extraction result for one document. Never edited in place."""

    __tablename__ = "extractions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), unique=True, index=True)
    stage_used: Mapped[str] = mapped_column(String(20))  # text / ocr / vision
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    vendor_text: Mapped[str | None] = mapped_column(String(300), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    tax: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    document: Mapped[Document] = relationship(back_populates="extraction")
    line_items: Mapped[list["ExtractionLineItem"]] = relationship(back_populates="extraction")


class ExtractionLineItem(Base):
    __tablename__ = "extraction_line_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    extraction_id: Mapped[int] = mapped_column(ForeignKey("extractions.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    # GL prediction lands here in Week 2 (Day 10-11), with its own confidence.
    predicted_gl_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("gl_accounts.id"), nullable=True
    )
    gl_confidence: Mapped[float | None] = mapped_column(nullable=True)

    extraction: Mapped[Extraction] = relationship(back_populates="line_items")


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), unique=True, index=True)
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"), nullable=True)
    qbo_bill_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # set on QBO posting
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft / review / posted / rejected
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    document: Mapped[Document] = relationship(back_populates="bill")
    vendor: Mapped[Vendor | None] = relationship()


class Match(Base):
    """One three-way-match verdict: a bill against a purchase order."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("bills.id"), index=True)
    po_id: Mapped[int | None] = mapped_column(ForeignKey("purchase_orders.id"), nullable=True)
    match_type: Mapped[str] = mapped_column(String(20))  # exact / fuzzy / none
    qty_diff: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    price_diff: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    amount_diff: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(30), nullable=True)  # matched / mismatch / short_pay / no_po


class ReviewAction(Base):
    """Every human action on a document — the eval gold mine.

    A correction stores field + old + new, so the benchmark can measure
    exactly which fields the machine got wrong.
    """

    __tablename__ = "review_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    user_action: Mapped[str] = mapped_column(String(20))  # approve / correct / reject
    field: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class EvalRun(Base):
    """One benchmark run: field-level accuracy + auto-post rate, honestly measured."""

    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    benchmark_size: Mapped[int] = mapped_column(default=0)
    field_accuracy_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    auto_post_rate: Mapped[float | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
