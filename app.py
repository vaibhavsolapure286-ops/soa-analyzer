import streamlit as st
import pdfplumber
import re
from collections import defaultdict
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

    # ------------------------------
    # CUSTOMER NAME
    # ------------------------------

    customer_name = "Not Found"

    customer_match = re.search(
        r'Ledger:\s*Mr[s]?\.\s*([^\n]+)',
        text
    )

    if customer_match:
        customer_name = (
            customer_match.group(1)
            .split("-")[0]
            .strip()
        )

    # ------------------------------
    # EMI RECEIPTS
    # ------------------------------

    receipt_count = text.lower().count("receipt")

    # ------------------------------
    # BOUNCES
    # ------------------------------

    bounce_count = (
        text.lower().count("bounced return")
    )

    # ------------------------------
    # BOUNCE CHARGES
    # ------------------------------

    bounce_charge_count = (
        text.lower().count("emi bouncing charges")
    )

    # ------------------------------
    # PARTIAL PAYMENT
    # ------------------------------

    partial_payment_count = 0

    if "pending" in text.lower():
        partial_payment_count += 1

    # ------------------------------
    # CURRENT POS
    # ------------------------------

    pos_match = re.findall(
        r'(\d+\.\d+)\s*Dr',
        text
    )

    current_pos = "Not Found"

    if pos_match:
        current_pos = pos_match[-1]

    # ------------------------------
    # MONTH-WISE DEBIT CREDIT
    # ------------------------------

    monthly_credit = defaultdict(float)
    monthly_debit = defaultdict(float)

    for line in text.split("\n"):

        date_match = re.search(
            r'(\d{2}-[A-Za-z]{3}-\d{2})',
            line
        )

        amounts = re.findall(
            r'(\d+\.\d+)',
            line
        )

        if date_match and amounts:

            try:

                txn_date = datetime.strptime(
                    date_match.group(1),
                    "%d-%b-%y"
                )

                month_key = txn_date.strftime(
                    "%b-%Y"
                )

                amount = float(
                    amounts[-1]
                )

                if (
                    "Receipt" in line
                    or "Received" in line
                ):
                    monthly_credit[month_key] += amount
                else:
                    monthly_debit[month_key] += amount

            except:
                pass

    debit_more = []
    credit_more = []

    for month in sorted(
        set(
            list(monthly_credit.keys()) +
            list(monthly_debit.keys())
        )
    ):

        debit = monthly_debit.get(
            month,
            0
        )

        credit = monthly_credit.get(
            month,
            0
        )

        if debit > credit:

            shortfall = debit - credit

            debit_more.append(
                f"{month} | Debit ₹{debit:,.0f} | Credit ₹{credit:,.0f} | Shortfall ₹{shortfall:,.0f}"
            )

        elif credit > debit:

            excess = credit - debit

            credit_more.append(
                f"{month} | Debit ₹{debit:,.0f} | Credit ₹{credit:,.0f} | Excess Credit ₹{excess:,.0f}"
            )

    debit_credit_summary = (
        "\n".join(debit_more)
        if debit_more
        else "None"
    )

    credit_debit_summary = (
        "\n".join(credit_more)
        if credit_more
        else "None"
    )

    # ------------------------------
    # OVERDUE
    # ------------------------------

    current_overdue = "Requires Manual Verification"

    # ------------------------------
    # FINAL OBSERVATION
    # ------------------------------

    observation = f"""
Customer Name : {customer_name}

EMI Entries Found : {receipt_count}

Bounce Count : {bounce_count}

Bounce Charge Count : {bounce_charge_count}

Partial Payment Count : {partial_payment_count}

Current POS : ₹{current_pos}

Current Overdue : {current_overdue}

Months Where Debit > Credit :

{debit_credit_summary}

Months Where Credit > Debit :

{credit_debit_summary}

Total Months Where Debit > Credit :
{len(debit_more)}

Total Months Where Credit > Debit :
{len(credit_more)}

FINAL OBSERVATION :

Customer repayment behaviour reviewed as per available SOA; EMI payment entries observed are {receipt_count}; total bounce count observed is {bounce_count}; bounce charge entries observed are {bounce_charge_count}; partial payment count observed is {partial_payment_count}; current POS observed is ₹{current_pos}; debit exceeded credit in {len(debit_more)} month(s) and credit exceeded debit in {len(credit_more)} month(s); current overdue requires verification against bounce recovery entries; overall repayment behaviour should be assessed based on bounce regularisation, overdue clearance status and payment continuity.
"""

    st.text_area(
        "SOA Analysis",
        observation,
        height=700
    )

    st.download_button(
        "Download Observation",
        observation,
        file_name="soa_observation.txt"
    )
