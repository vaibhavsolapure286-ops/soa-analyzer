import streamlit as st
import pdfplumber
import re

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

    if "Pending" in text:
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
    # OVERDUE
    # ------------------------------

    current_overdue = "Check Bounce Recovery"

    # ------------------------------
    # FINAL OBSERVATION
    # ------------------------------

    observation = f"""
Customer Name: {customer_name}

EMI Payments Observed: {receipt_count}

Bounce Count: {bounce_count}

Bounce Charge Entries: {bounce_charge_count}

Partial Payment Count: {partial_payment_count}

Current POS: ₹{current_pos}

Current Overdue: {current_overdue}

Final Observation:

Customer repayment behaviour reviewed as per available SOA; EMI payment entries observed are {receipt_count}; total bounce count observed is {bounce_count}; bounce charge entries observed are {bounce_charge_count}; partial payment count observed is {partial_payment_count}; current POS is ₹{current_pos}; current overdue requires verification against bounce recovery entries; overall repayment behaviour should be assessed based on bounce regularisation, overdue clearance status and payment continuity.
"""

    st.text_area(
        "SOA Analysis",
        observation,
        height=400
    )

    st.download_button(
        "Download Observation",
        observation,
        file_name="soa_observation.txt"
    )
`
