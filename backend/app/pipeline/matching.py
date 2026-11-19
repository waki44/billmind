"""Three-way match + duplicate detection — Week 2, Day 12.

Three-way match: invoice <-> purchase order <-> amounts.
- Match the vendor first (rapidfuzz over vendors.normalised_name), then the
  PO by reference number, then compare quantities / prices / totals.
- Record qty_diff, price_diff, amount_diff and a verdict on the matches
  table: matched / mismatch / short_pay / no_po.

Duplicate detection: same vendor + invoice number + total — exact first,
then fuzzy (a re-sent invoice with a slightly different scan is still a
duplicate).

TODO(WAQAR): the diff tolerances are judgment calls. Zero tolerance sounds
safe and floods the review queue; loose tolerance lets wrong bills through.
Pick them from what the benchmark set shows, and be able to defend each one.
"""


def find_po_for_invoice(extraction) -> dict:
    """Return the match result dict for one extraction (see models.Match)."""
    raise NotImplementedError("Week 2, Day 12 — three-way match is judgment-layer work.")


def is_duplicate(extraction, db) -> bool:
    """Exact + fuzzy duplicate check against previously seen extractions."""
    raise NotImplementedError("Week 2, Day 12 — duplicate detection is judgment-layer work.")
