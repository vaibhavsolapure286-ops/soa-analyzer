"""
analyze_soa.py
----------------
Reads a Tally-style Loan Account Statement-of-Account (SOA) text export and
produces an EMI-compliance analysis for the borrower:

  1. Late EMI payments   - EMI for a given month actually credited/received
                            in a LATER calendar month, with date & amount.
  2. Cheque / E-NACH bounces - every bounce event, the month it relates to,
                            and a running bounce count.
  3. Partial payments    - months where the EMI due (Rs.15,790) was received
                            through more than one part-payment / receipt.
  4. Current POS         - loan outstanding balance as per the last ledger
                            entry (Principal Outstanding, i.e. the closing
                            Dr balance of the account).

Usage:
    python analyze_soa.py ledger.txt

Output:
    Prints a console summary AND writes soa_analysis.xlsx with the details.
"""

import re
import sys
from datetime import datetime
from collections import defaultdict

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}
# common abbreviations / misspellings seen in the SOA
MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "febraury": 2,  # typo present in source SOA
}

DATE_RE = re.compile(r'^(\d{2})-([A-Za-z]{3})-(\d{2})\b')
EMI_AMOUNT = 15790.00  # standard EMI as seen throughout the SOA


def month_num(word):
    w = word.lower().strip('.')
    if w in MONTH_ALIASES:
        return MONTH_ALIASES[w]
    for full, num in MONTHS.items():
        if full.startswith(w):
            return num
    return None


def parse_date(datestr):
    # e.g. 08-Dec-22
    return datetime.strptime(datestr, "%d-%b-%y")


def load_records(path):
    """Split the raw ledger text into transaction records.
    A new record starts at a line beginning with DD-Mon-YY."""
    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]

    records = []
    current = None
    for line in lines:
        if DATE_RE.match(line):
            if current:
                records.append(current)
            current = {"header": line, "body": []}
        else:
            if current is not None:
                current["body"].append(line)
    if current:
        records.append(current)
    return records


def extract_amount_and_balance(header):
    """Pull the transaction amount and running balance off the header line."""
    nums = re.findall(r'[\d,]+\.\d{2}', header)
    nums = [float(n.replace(",", "")) for n in nums]
    amount = nums[0] if len(nums) >= 1 else None
    balance = nums[-1] if len(nums) >= 1 else None
    is_dr_balance = header.strip().endswith("Dr")
    return amount, balance, is_dr_balance


def build_transactions(records):
    txns = []
    for rec in records:
        m = DATE_RE.match(rec["header"])
        date = parse_date(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
        amount, balance, is_dr = extract_amount_and_balance(rec["header"])
        narration = " ".join(rec["body"]).strip()
        txns.append({
            "date": date,
            "header": rec["header"],
            "narration": narration,
            "amount": amount,
            "balance": balance,
            "balance_is_dr": is_dr,
        })
    return txns


def covering_month(narration):
    """Extract the (month, year) an EMI/interest/bounce narration refers to,
    from phrases like 'for the month of December 2022' or 'm/o November 2022'."""
    pat = re.search(
        r'(?:for the month of|m/o)\s+([A-Za-z]+)\.?\s+(\d{4})',
        narration, re.IGNORECASE)
    if not pat:
        return None
    mn = month_num(pat.group(1))
    yr = int(pat.group(2))
    if mn is None:
        return None
    return (yr, mn)


def analyze(txns):
    emi_events = []       # every receipt/IMPS credited towards an EMI month
    bounce_events = []    # every bounce related entry
    interest_by_month = {}

    for t in txns:
        narr = t["narration"]
        low = narr.lower()

        cm = covering_month(narr)

        is_bounce = bool(re.search(r'bounc', low))
        is_emi_payment = bool(re.search(
            r'emi received|e-nach presented|imps received|cheque received towards bpi',
            low))
        is_interest_booking = bool(re.search(r'interest booked', low))

        if is_bounce and cm:
            bounce_events.append({
                "date": t["date"], "month": cm, "amount": t["amount"],
                "narration": narr,
            })

        if is_emi_payment and cm:
            emi_events.append({
                "date": t["date"], "month": cm, "amount": t["amount"],
                "narration": narr,
            })

        if is_interest_booking and cm:
            interest_by_month[cm] = t["date"]

    # ---- group EMI receipts by the month they were meant to cover ----
    emi_by_month = defaultdict(list)
    for e in emi_events:
        emi_by_month[e["month"]].append(e)

    late_payments = []
    partial_payments = []

    for month, events in sorted(emi_by_month.items()):
        yr, mn = month
        events_sorted = sorted(events, key=lambda x: x["date"])
        total_received = sum(e["amount"] for e in events_sorted if e["amount"])
        # due date convention observed throughout: the 8th of the EMI month
        due_date = datetime(yr, mn, 8)

        # Late = the (first/only) qualifying receipt landed in a different
        # calendar month/year than the EMI's own due month.
        first_event = events_sorted[0]
        if (first_event["date"].year, first_event["date"].month) != (yr, mn):
            late_payments.append({
                "emi_month": f"{due_date.strftime('%B %Y')}",
                "due_date": due_date.strftime("%d-%b-%Y"),
                "actual_payment_date": first_event["date"].strftime("%d-%b-%Y"),
                "amount": first_event["amount"],
                "days_late": (first_event["date"] - due_date).days,
            })

        # Partial = more than one receipt line was needed to cover the month
        if len(events_sorted) > 1:
            partial_payments.append({
                "emi_month": due_date.strftime("%B %Y"),
                "num_parts": len(events_sorted),
                "parts": [
                    (e["date"].strftime("%d-%b-%Y"), e["amount"])
                    for e in events_sorted
                ],
                "total_received": total_received,
            })

    # ---- bounce count per month + running total ----
    bounce_by_month = defaultdict(list)
    for b in bounce_events:
        bounce_by_month[b["month"]].append(b)

    bounce_summary = []
    running_total = 0
    for month, events in sorted(bounce_by_month.items()):
        yr, mn = month
        running_total += len(events)
        for e in events:
            bounce_summary.append({
                "month": datetime(yr, mn, 1).strftime("%B %Y"),
                "date": e["date"].strftime("%d-%b-%Y"),
                "amount": e["amount"],
                "narration": e["narration"][:90],
                "running_bounce_count": running_total,
            })

    # ---- current POS = balance of the very last ledger entry ----
    last_txn = max(txns, key=lambda t: t["date"])
    current_pos = last_txn["balance"]
    pos_as_on = last_txn["date"].strftime("%d-%b-%Y")

    return {
        "late_payments": late_payments,
        "partial_payments": partial_payments,
        "bounce_summary": bounce_summary,
        "total_bounces": len(bounce_events),
        "current_pos": current_pos,
        "pos_as_on": pos_as_on,
    }


def print_report(result):
    print("=" * 70)
    print("LATE EMI PAYMENTS (paid in a month after the EMI was due)")
    print("=" * 70)
    if not result["late_payments"]:
        print("None found.")
    for lp in result["late_payments"]:
        print(f"EMI Month: {lp['emi_month']:<15} Due: {lp['due_date']}  "
              f"Paid: {lp['actual_payment_date']}  Amount: Rs.{lp['amount']:,.2f}  "
              f"({lp['days_late']} days late)")

    print()
    print("=" * 70)
    print(f"CHEQUE / E-NACH BOUNCES  (Total: {result['total_bounces']})")
    print("=" * 70)
    if not result["bounce_summary"]:
        print("None found.")
    for b in result["bounce_summary"]:
        print(f"Date: {b['date']}  Month: {b['month']:<12} "
              f"Amount: Rs.{b['amount']:,.2f}  Running Count: {b['running_bounce_count']}")
        print(f"   -> {b['narration']}")

    print()
    print("=" * 70)
    print("PARTIAL PAYMENTS (EMI settled through more than one receipt)")
    print("=" * 70)
    if not result["partial_payments"]:
        print("None found.")
    for pp in result["partial_payments"]:
        parts_str = ", ".join(f"{d}: Rs.{a:,.2f}" for d, a in pp["parts"])
        print(f"EMI Month: {pp['emi_month']:<15} Parts: {pp['num_parts']}  "
              f"Total Received: Rs.{pp['total_received']:,.2f}")
        print(f"   -> {parts_str}")

    print()
    print("=" * 70)
    print("CURRENT POS (Principal Outstanding as per last ledger entry)")
    print("=" * 70)
    print(f"As on {result['pos_as_on']}: Rs.{result['current_pos']:,.2f} Dr")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "ledger.txt"
    records = load_records(path)
    txns = build_transactions(records)
    result = analyze(txns)
    print_report(result)

    # Save result for downstream Excel export
    import json
    with open("analysis_result.json", "w") as f:
        json.dump(result, f, default=str, indent=2)
