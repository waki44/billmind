"""GL coding prediction — Week 2, Day 10-11.

Embed the descriptions of past bills' line items (sentence embeddings over
the business's own posting history); for a new line item, suggest the account
of its nearest neighbours, store it on extraction_line_items as
predicted_gl_account_id + gl_confidence, and SHOW THE REASON in the review
queue ('coded to 5200 Cloud Hosting because 4 past bills from this vendor
with similar descriptions went there').

A prediction with a shown reason is a senior feature; a bare prediction is a
party trick. Cold start (little history) is expected to be weak — the review
queue exists for exactly that.

TODO(WAQAR): embedding model choice, neighbour count, and when a vendor's
default_gl_account_id should override the embedding vote are your calls.
"""


def predict_gl_account(line_item_description: str, vendor_id: int | None, db) -> dict:
    """Return {'gl_account_id': int|None, 'confidence': float, 'reason': str}."""
    raise NotImplementedError("Week 2, Day 10-11 — GL prediction is judgment-layer work.")
