"""Creates the sample documents in samples/ and their answer key, golden.json.

The invoices are drawn from the data below, so we know the correct answer for every field.
That is what makes them a golden dataset. You don't need to run this: samples/ is committed.

    python make_samples.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter

OUT = Path("samples")
OUT.mkdir(exist_ok=True)

INVOICES = [
    {"file": "invoice_01.png", "style": "clean",
     "vendor_name": "Sharma Electronics", "invoice_number": "INV-2026-0412", "invoice_date": "2026-09-14",
     "date_shown": "14/09/2026", "currency": "INR", "tax_rate": 18,
     "items": [("USB-C cable 1m", 3, 299.00), ("Wireless mouse", 1, 899.00)]},
    {"file": "invoice_02.png", "style": "right",
     "vendor_name": "Kapoor Stationers", "invoice_number": "KS/889", "invoice_date": "2026-10-02",
     "date_shown": "02 Oct 2026", "currency": "INR", "tax_rate": 12,
     "items": [("A4 paper ream", 5, 320.00), ("Gel pens (box of 10)", 2, 150.00),
               ("Stapler", 1, 245.00), ("Sticky notes", 6, 40.00)]},
    {"file": "invoice_03.png", "style": "photo",
     "vendor_name": "Mehta Hardware", "invoice_number": "MH-7731", "invoice_date": "2026-08-27",
     "date_shown": "27-08-2026", "currency": "INR", "tax_rate": 18,
     "items": [("Hammer", 2, 385.00), ("Screws (pack of 100)", 3, 120.00), ("Measuring tape 5m", 1, 210.00)]},
    {"file": "invoice_04.png", "style": "clean",
     "vendor_name": "Gupta Caterers", "invoice_number": "GC-0098", "invoice_date": "2026-09-30",
     "date_shown": "30/09/2026", "currency": "INR", "tax_rate": 5,
     "items": [("Veg thali", 20, 180.00), ("Masala chai", 40, 25.00)],
     "total_typo": 100.00},   # the vendor printed a wrong total: extraction is right, the business rule must catch it
    {"file": "invoice_05.pdf", "style": "clean",
     "vendor_name": "CloudNine Software LLC", "invoice_number": "CN-2026-117", "invoice_date": "2026-10-05",
     "date_shown": "October 5, 2026", "currency": "USD", "tax_rate": 0,
     "items": [("Pro plan, 10 seats (monthly)", 10, 12.00), ("Priority support", 1, 49.00)]},
    {"file": "invoice_06.png", "style": "dense",
     "vendor_name": "Fresh Basket Grocers", "invoice_number": "FB-55120", "invoice_date": "2026-10-11",
     "date_shown": "11.10.2026", "currency": "INR", "tax_rate": 5,
     "items": [("Basmati rice 5kg", 1, 649.00), ("Toor dal 1kg", 2, 168.00), ("Sunflower oil 1L", 3, 145.00),
               ("Atta 10kg", 1, 455.00), ("Sugar 1kg", 2, 48.00), ("Tea 500g", 1, 290.00),
               ("Paneer 200g", 4, 95.00), ("Curd 400g", 2, 45.00)]},
]


def totals(inv):
    subtotal = round(sum(q * p for _, q, p in inv["items"]), 2)
    tax = round(subtotal * inv["tax_rate"] / 100, 2)
    return subtotal, tax, round(subtotal + tax + inv.get("total_typo", 0), 2)


def money(x, cur):
    return f"{'$' if cur == 'USD' else 'Rs.'} {x:,.2f}"


def draw_invoice(inv, path):
    sub, tax, total = totals(inv)
    cur = inv["currency"]
    fs = 8.5 if inv["style"] == "dense" else 10
    fig = plt.figure(figsize=(6, 7.5), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    right = inv["style"] == "right"
    x0, ha = (0.92, "right") if right else (0.08, "left")
    ax.text(x0, 0.93, inv["vendor_name"], fontsize=16, weight="bold", ha=ha)
    ax.text(x0, 0.895, "12, Main Market Road, New Delhi" if cur == "INR" else "500 Market St, San Francisco, CA",
            fontsize=8, color="#555", ha=ha)
    ax.text(0.92 if not right else 0.08, 0.93, "TAX INVOICE" if cur == "INR" else "INVOICE",
            fontsize=13, weight="bold", ha="right" if not right else "left", color="#1f4e79")
    ax.text(0.08, 0.83, f"Invoice No: {inv['invoice_number']}", fontsize=fs)
    ax.text(0.08, 0.80, f"Date: {inv['date_shown']}", fontsize=fs)
    ax.text(0.92, 0.83, "Bill to: Acme Labs Pvt Ltd", fontsize=fs, ha="right")

    y = 0.73
    ax.plot([0.08, 0.92], [y + 0.025, y + 0.025], color="#333", lw=1)
    for x, h, a in [(0.08, "Description", "left"), (0.60, "Qty", "right"), (0.76, "Rate", "right"), (0.92, "Amount", "right")]:
        ax.text(x, y, h, fontsize=fs, weight="bold", ha=a)
    ax.plot([0.08, 0.92], [y - 0.015, y - 0.015], color="#333", lw=1)
    step = 0.04 if inv["style"] == "dense" else 0.05
    for desc, q, p in inv["items"]:
        y -= step
        ax.text(0.08, y, desc, fontsize=fs)
        ax.text(0.60, y, str(q), fontsize=fs, ha="right")
        ax.text(0.76, y, f"{p:,.2f}", fontsize=fs, ha="right")
        ax.text(0.92, y, f"{q * p:,.2f}", fontsize=fs, ha="right")
    y -= 0.03
    ax.plot([0.55, 0.92], [y, y], color="#333", lw=1)
    tax_label = f"GST @ {inv['tax_rate']}%" if cur == "INR" else f"Sales tax ({inv['tax_rate']}%)"
    for label, val, bold in [("Subtotal", sub, False), (tax_label, tax, False), ("TOTAL", total, True)]:
        y -= 0.045
        ax.text(0.60, y, label, fontsize=fs + (1 if bold else 0), weight="bold" if bold else "normal")
        ax.text(0.92, y, money(val, cur), fontsize=fs + (1 if bold else 0), ha="right", weight="bold" if bold else "normal")
    ax.text(0.5, 0.05, "Thank you for your business!", fontsize=8, ha="center", color="#777")
    fig.savefig(path)
    plt.close(fig)


def make_photo(path):
    """Make a clean render look like a bad phone photo: small, tilted, blurry, grey."""
    img = Image.open(path).convert("L")
    img = img.resize((img.width * 2 // 5, img.height * 2 // 5))
    img = img.rotate(4, expand=True, fillcolor=170).filter(ImageFilter.GaussianBlur(1.1))
    img = img.point(lambda v: int(v * 0.8 + 30))
    img.save(path)


def draw_chart(path):
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
    revenue = [4.2, 4.8, 3.9, 5.6, 6.1, 7.3]
    fig, ax = plt.subplots(figsize=(6, 3.6), dpi=150)
    bars = ax.bar(months, revenue, color="#4dabf7")
    ax.bar_label(bars, fmt="%.1f")
    ax.set_title("Monthly revenue, FY 2026-27 (Rs. lakh)")
    ax.set_ylabel("Rs. lakh"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    golden = []
    for inv in INVOICES:
        path = OUT / inv["file"]
        draw_invoice(inv, path)
        if inv["style"] == "photo":
            make_photo(path)
        sub, tax, total = totals(inv)
        golden.append({
            "file": inv["file"],
            "expected": {
                "vendor_name": inv["vendor_name"], "invoice_number": inv["invoice_number"],
                "invoice_date": inv["invoice_date"], "currency": inv["currency"],
                "line_items": [{"description": d, "quantity": q, "unit_price": p, "amount": round(q * p, 2)}
                               for d, q, p in inv["items"]],
                "subtotal": sub, "tax": tax, "total": total,
            },
            # the business rule that SHOULD fire on this document (empty = the document is fine)
            "expected_rule_errors": ["total_mismatch"] if "total_typo" in inv else [],
        })
    draw_chart(OUT / "revenue_chart.png")
    # the same invoice 06 as a "scanned" PDF: an image inside a PDF, no text layer
    Image.open(OUT / "invoice_06.png").convert("RGB").save(OUT / "scanned_invoice.pdf")
    Path("golden.json").write_text(json.dumps(golden, indent=2))
    print(f"wrote {len(golden)} invoices, 1 chart, 1 scanned PDF to {OUT}/ and golden.json")
