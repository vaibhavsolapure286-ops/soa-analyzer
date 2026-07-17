import streamlit as st
import pdfplumber
import re
from datetime import datetime

st.set_page_config(page_title="SOA Analyzer")

st.title("SOA Analyzer")

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

    # ---------------------------------
    # Customer Name
    # ---------------------------------

    customer_name = "Not Found"

    customer_match = re.search(
        r'Ledger:\s*Mr\.\s*([^\n]+)',
        text
    )

    if customer_match:
        customer_name = (
            customer_match
            .group(1)
            .split("-")[0]
            .strip()
        )

    # ---------------------------------
    # Receipts
    # ---------------------------------

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

    emi_amount = None

    if receipts:
        emi_amount = receipts[0][1]

    # ---------------------------------
    # Partial Payments
    # ---------------------------------

    partial_payments = []

    if emi_amount:

        for date, amount in receipts:

            if amount < emi_amount:

                partial_payments.append(
                    (date, amount)
                )

    # ---------------------------------
    # Bulk Payments
    # ---------------------------------

    bulk_payments = []

    if emi_amount:

        for date, amount in receipts:

            if amount >= (emi_amount * 2):

                bulk_payments.append(
                    (date, amount)
                )

    # ---------------------------------
    # Bounce Detection
    # ---------------------------------

    bounce_details = []

    lines = text.split("\n")

    for line in lines:

        if (
            "Bounced Return" in line
            or "Bounce" in line
            or "insufficient fund" in line.lower()
        ):

            date_match = re.search(
                r'(\d{2}-[A-Za-z]{3}-\d{2})',
                line
            )

            amount_match = re.search(
                r'(\d+\.\d+)',
                line
            )

            if date_match:

                bounce_date = date_match.group(1)

                bounce_amount = (
                    float(amount_match.group(1))
                    if amount_match
                    else emi_amount
                )

                bounce_details.append(
                    {
                        "date": bounce_date,
                        "amount": bounce_amount
                    }
                )

    # ---------------------------------
    # Bounce Recovery Logic
    # ---------------------------------

    cleared_bounce_count = 0
    pending_bounce_count = 0

    bounce_summary = []

    for bounce in bounce_details:

        bounce_date = datetime.strptime(
            bounce["date"],
            "%d-%b-%y"
        )

        recovery_found = False

        for receipt_date, receipt_amt in receipts:

            r_date = datetime.strptime(
                receipt_date,
                "%d-%b-%y"
            )

            if r_date > bounce_date:

                recovery_found = True

                cleared_bounce_count += 1

                bounce_summary.append(
                    f"Bounce of ₹{bounce['amount']:,.0f} on {bounce['date']} cleared on {receipt_date} by payment of ₹{receipt_amt:,.0f}"
                )

                break

        if not recovery_found:

            pending_bounce_count += 1

            bounce_summary.append(
                f"Bounce of ₹{bounce['amount']:,.0f} on {bounce['date']} remains uncleared"
            )

    # ---------------------------------
    # Current Overdue
    # ---------------------------------

    current_overdue = 0

    for bounce in bounce_details:

        bounce_date = datetime.strptime(
            bounce["date"],
            "%d-%b-%y"
        )

        recovered = False

        for receipt_date, receipt_amt in receipts:

            r_date = datetime.strptime(
                receipt_date,
                "%d-%b-%y"
            )

            if r_date > bounce_date:

                recovered = True
                break

        if not recovered:

            current_overdue += (
                bounce["amount"]
                if bounce["amount"]
                else 0
            )

    # ---------------------------------
    # Estimated DPD
    # ---------------------------------

    current_dpd_days = 0

    if bounce_details:

        last_pending_date = None

        for bounce in bounce_details:

            bounce_date = datetime.strptime(
                bounce["date"],
                "%d-%b-%y"
            )

            recovered = False

            for receipt_date, _ in receipts:

                r_date = datetime.strptime(
                    receipt_date,
                    "%d-%b-%y"
                )

                if r_date > bounce_date:

                    recovered = True
                    break

            if not recovered:
                last_pending_date = bounce_date

        if last_pending_date:

            current_dpd_days = (
                datetime.today()
                - last_pending_date
            ).days

    current_dpd_months = round(
        current_dpd_days / 30,
        1
    )

    # ---------------------------------
    # Behaviour
    # ---------------------------------

    if (
        len(bounce_details) == 0
        and current_overdue == 0
    ):

        behaviour = "Regular"

    elif (
        len(bounce_details) > 0
        and current_overdue == 0
    ):

        behaviour = "Irregular with historical bounce instances"

    else:

        behaviour = "Irregular"

    # ---------------------------------
    # Final Observation
    # ---------------------------------

    bounce_count = len(bounce_details)

    if current_overdue > 0:

        status = (
            "customer has not cleared the delinquency"
        )

    else:

        status = (
            "customer has cleared the delinquency"
        )

    final_observation = f"""
Customer Name: {customer_name}

Total Bounce Count: {bounce_count}

Cleared Bounce Count: {cleared_bounce_count}

Pending Bounce Count: {pending_bounce_count}

Current Overdue Amount: ₹{current_overdue:,.0f}

Estimated Current DPD: {current_dpd_days} days ({current_dpd_months} months)

Final Observation:

Customer paid EMI of ₹{emi_amount:,.0f} regularly; total bounce count observed is {bounce_count}; {'; '.join(bounce_summary) if bounce_summary else 'no bounce observed'}; partial payment count observed is {len(partial_payments)}; bulk payment count observed is {len(bulk_payments)}; current overdue amount is ₹{current_overdue:,.0f}; estimated current DPD is {current_dpd_days} days ({current_dpd_months} months); {status}; repayment behaviour is {behaviour}.
"""

    st.text_area(
        "Analysis Result",
        final_observation,
        height=450
    )
