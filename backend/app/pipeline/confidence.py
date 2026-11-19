"""Composite confidence score — Week 2, Day 13-14.

TODO(WAQAR): this formula is the heart of the project. Design it, calibrate
it against the frozen benchmark set, and write the reasoning in the README —
'how did you calibrate 85%?' is THE interview question for this project.

Signals available to combine (Week 2, Day 8-9 collects them):
- which extraction stage produced the fields (text > ocr > vision, usually)
- OCR quality / per-field extraction confidence
- cross-checks: subtotal + tax == total, line items sum to subtotal
- vendor recognised? invoice number seen before (duplicate risk)?
- three-way match verdict (see matching.py)

HARD GATE (roadmap section 8 — not negotiable, not a tuning choice):
if the totals do not reconcile, the document can NEVER auto-post, whatever
the composite score says. Implement totals_reconcile() first and check it
before the score is even consulted.
"""
from decimal import Decimal


def totals_reconcile(subtotal: Decimal | None, tax: Decimal | None, total: Decimal | None) -> bool:
    """True only if subtotal + tax == total (within a cent). None anywhere = False."""
    raise NotImplementedError("Hard gate — implement before the score (Week 2).")


def composite_confidence(signals: dict) -> float:
    """Combine the per-field/per-document signals into one 0..1 score."""
    raise NotImplementedError("Week 2, Day 13-14 — calibrate against the benchmark set.")
