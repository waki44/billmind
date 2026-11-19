"""Document classification — Week 1, Day 4.

TODO(WAQAR): classify each attachment as invoice / purchase_order /
remittance / other.

Planned approach (from the roadmap): rules first (filename, sender, keyword
signals), LLM fallback for the ambiguous ones. Decide the rule order yourself
and be ready to explain why — 'which signal do you trust first, and what does
a misclassification cost downstream?' is an interview question.

Returns one of: 'invoice', 'purchase_order', 'remittance', 'other'.
"""


def classify_document(file_path: str, raw_text: str | None) -> str:
    raise NotImplementedError("Week 1, Day 4 — classification is judgment-layer work.")
