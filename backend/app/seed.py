"""Day-1 seed data: a small chart of accounts, 3 vendors, sample POs.

Generic demo business (an IT/services firm) so the pipeline and the GL
prediction have something realistic to work against from Day 2 onward.
Idempotent: running it twice does not duplicate rows.

Run:  python -m app.seed
"""
import re
from datetime import date
from decimal import Decimal

from .db import SessionLocal, init_db
from .models import GLAccount, POLineItem, PurchaseOrder, Vendor

CHART_OF_ACCOUNTS = [
    ("5000", "Office Supplies"),
    ("5100", "Software Subscriptions"),
    ("5200", "Cloud Hosting & Infrastructure"),
    ("5300", "Professional Services"),
    ("5400", "Equipment & Hardware"),
    ("6000", "Rent"),
    ("6100", "Utilities"),
    ("6200", "Marketing & Advertising"),
]

# (name, tax_id, default GL code)
VENDORS = [
    ("CloudServe Hosting (Pvt) Ltd", "3849201-7", "5200"),
    ("TechMart Supplies", "2918473-2", "5400"),
    ("BrightPrint Studio", "4729105-9", "6200"),
]

# (vendor name, po_number, order_date, [(description, qty, unit_price)])
PURCHASE_ORDERS = [
    (
        "CloudServe Hosting (Pvt) Ltd",
        "PO-2026-001",
        date(2026, 11, 2),
        [("VPS hosting — November 2026", Decimal("1"), Decimal("45000"))],
    ),
    (
        "TechMart Supplies",
        "PO-2026-002",
        date(2026, 11, 5),
        [
            ("Wireless keyboard", Decimal("5"), Decimal("6500")),
            ("Wireless mouse", Decimal("5"), Decimal("4200")),
        ],
    ),
    (
        "BrightPrint Studio",
        "PO-2026-003",
        date(2026, 11, 9),
        [("Event banner printing (6x3 ft)", Decimal("2"), Decimal("8500"))],
    ),
]


def normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()


def seed(db) -> dict:
    accounts: dict[str, GLAccount] = {}
    for code, name in CHART_OF_ACCOUNTS:
        acct = db.query(GLAccount).filter_by(code=code).first()
        if acct is None:
            acct = GLAccount(code=code, name=name)
            db.add(acct)
            db.flush()
        accounts[code] = acct

    vendors: dict[str, Vendor] = {}
    for name, tax_id, default_code in VENDORS:
        vendor = db.query(Vendor).filter_by(normalised_name=normalise(name)).first()
        if vendor is None:
            vendor = Vendor(
                name=name,
                normalised_name=normalise(name),
                tax_id=tax_id,
                default_gl_account_id=accounts[default_code].id,
            )
            db.add(vendor)
            db.flush()
        vendors[name] = vendor

    po_count = 0
    for vendor_name, po_number, order_date, items in PURCHASE_ORDERS:
        if db.query(PurchaseOrder).filter_by(po_number=po_number).first() is not None:
            continue
        total = sum(qty * price for _, qty, price in items)
        po = PurchaseOrder(
            vendor_id=vendors[vendor_name].id,
            po_number=po_number,
            order_date=order_date,
            total=total,
            status="open",
        )
        db.add(po)
        db.flush()
        for description, qty, price in items:
            db.add(
                POLineItem(
                    po_id=po.id,
                    description=description,
                    qty=qty,
                    unit_price=price,
                    amount=qty * price,
                )
            )
        po_count += 1

    db.commit()
    return {
        "gl_accounts": len(accounts),
        "vendors": len(vendors),
        "purchase_orders_created": po_count,
    }


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        print(seed(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
