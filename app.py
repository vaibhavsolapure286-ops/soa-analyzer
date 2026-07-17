import streamlit as st
import pdfplumber
import re
from datetime import datetime

st.set_page_config(page_title="SOA Review Analyzer")

st.title("SOA Review Analyzer")

pdf_file = st.file_uploader(
    "Upload SOA PDF",
    type=["pdf"]
)

if pdf_file:

    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    # -------------------------
    # CUSTOMER NAME
    # -------------------------

    customer_name = "Not Found"

    match = re.search(
        r'Ledger:\s*Mr\.\s*([^\n]+)',
        text
    )

    if match:
        customer_name = match.group(1).split("-")[0].strip()

    # -------------------------
    # PAYMENTS
    # -------------------------

    receipt_pattern = r'(\d{2}-[A-Za-z]{3}-\d{2}).*?Receipt.*?(\d+\.\d+)'

    receipts = []

    for m in re.finditer(
        receipt_pattern,
        text
    ):
        receipts.append(
            (
                m.group(1),
                float(m.group(2))
            )
        )

    emi_amount = 0

    if receipts:
        emi_amount = receipts[0][1]

    # -------------------------
    # BOUNCES
    # -------------------------

    bounce_dates = []
    bounce_amounts = []

    for line in text.split("\n"):

        if (
            "Bounced Return" in line
            or "Bounce" in line
            or "insufficient fund" in line.lower()
        ):

            date_match = re.search(
                r'(\d{2}-[A-Za-z]{3}-\d{2})',
                line
            )

            amt_match = re.search(
                r'(\d+\.\d+)',
                line
            )

            if date_match:

                bounce_dates.append(
                    date_match.group(1)
                )

                if amt_match:
                    bounce_amounts.append(
                        float(
                            amt_match.group(1)
                        )
                    )
                else:
                    bounce_amounts.append(
                        emi_amount
                    )

    total_bounces = len(bounce_dates)

    # -------------------------
    # BOUNCE RECOVERY
    # -------------------------

    cleared = 0
    pending = 0

    bounce_summary = []

    for i in range(len(bounce_dates)):

        bounce_date = datetime.strptime(
            bounce_dates[i],
            "%d-%b-%y"
        )

        recovered = False

        for receipt_date, receipt_amt in receipts:

            payment_date = datetime.strptime(
                receipt_date,
                "%d-%b-%y"
            )

            if payment_date > bounce_date:

                recovered = True
                cleared += 1

                bounce_summary.append(
                    f"Bounce on {bounce_dates[i]} cleared on {receipt_date} by payment of ₹{receipt_amt:,.0f}"
                )

                break

        if not recovered:

            pending += 1

            bounce_summary.append(
                f"Bounce on {bounce_dates[i]} remains uncleared"
            )

    # -------------------------
    # PARTIAL PAYMENT
    # -------------------------

    partial_count = 0

    for _, amt in receipts:

        if emi_amount > 0 and amt < emi_amount:
            partial_count += 1

    # -------------------------
    # BULK PAYMENT
    # -------------------------

    bulk_count = 0

    for _, amt in receipts:

        if emi_amount > 0 and amt >= emi_amount * 2:
            bulk_count += 1

    # -------------------------
    # PENALTY CHARGES
    # -------------------------

    penalty_count = 0

    penalty_keywords = [
        "bounce charges",
        "emi bouncing charges",
        "late payment charges",
        "penalty charges",
        "penal interest",
        "overdue charges"
    ]

    for line in text.split("\n"):

        for k in penalty_keywords:

            if k.lower() in line.lower():
                penalty_count += 1

    # -------------------------
    # NEGATIVE REMARKS
    # -------------------------

    negative_hits = []

    negative_words = [
        "default",
        "settlement",
        "write off",
        "write-off",
        "legal",
        "recovery",
        "repossession"
    ]

    for word in negative_words:

        if word.lower() in text.lower():
            negative_hits.append(word)

    # -------------------------
    # OVERDUE
    # -------------------------

    current_overdue = pending * emi_amount

    # -------------------------
    # DPD
    # -------------------------

    current_dpd_days = 0

    if pending > 0:

        oldest_pending = datetime.strptime(
            bounce_dates[-1],
            "%d-%b-%y"
        )

        current_dpd_days = (
            datetime.today()
            - oldest_pending
        ).days

    current_dpd_months = round(
        current_dpd_days / 30,
        1
    )

    # -------------------------
    # BEHAVIOUR
    # -------------------------

    if total_bounces == 0:

        behaviour = "Regular"

    elif pending == 0:

        behaviour = "Irregular with historical bounce instances"

    else:

        behaviour = "Irregular"

    # -------------------------
    # FINAL OBSERVATION
    # -------------------------

    final_text = f"""
Customer Name: {customer_name}

EMI Amount: ₹{emi_amount:,.0f}

Total Bounce Count: {total_bounces}

Cleared Bounce Count: {cleared}

Pending Bounce Count: {pending}

Partial Payment Count: {partial_count}

Bulk Payment Count: {bulk_count}

Penalty Charge Entries: {penalty_count}

Current Overdue: ₹{current_overdue:,.0f}

Estimated Current DPD: {current_dpd_days} days ({current_dpd_months} months)

Negative Remarks:
{', '.join(negative_hits) if negative_hits else 'None'}

Bounce Summary:
{' | '.join(bounce_summary) if bounce_summary else 'No bounce observed'}

FINAL OBSERVATION:

Customer repayment behaviour reviewed as per available SOA; EMI amount observed is ₹{emi_amount:,.0f}; total bounce count is {total_bounces}, cleared bounce count is {cleared} and pending bounce count is {pending}; partial payment count observed is {partial_count}; bulk payment count observed is {bulk_count}; penalty charge entries observed are {penalty_count}; current overdue amount is ₹{current_overdue:,.0f}; estimated current DPD is {current_dpd_days} days ({current_dpd_months} months); {'negative remarks observed: ' + ', '.join(negative_hits) if negative_hits else 'no negative remarks observed'}; overall repayment behaviour is assessed as {behaviour}.
"""

    st.text_area(
        "SOA Analysis",
        final_text,
        height=500
    )
