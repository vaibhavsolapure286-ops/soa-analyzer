import streamlit as st
import pdfplumber
import re
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
    customer_name = "Not Found"
    match = re.search(
        r'Ledger:\s*Mr[s]?\.\s*([^\n]+)',
        text
    )
    if match:
        customer_name = (
            match.group(1)
            .split("-")[0]
            .strip()
        )
    receipt_count = text.lower().count("receipt")
    bounce_count = (
        text.lower().count("bounced return")
    )
    bounce_charge_count = (
        text.lower().count("emi bouncing charges")
    )
    partial_payment_count = 0
    if "pending" in text.lower():
        partial_payment_count = 1
    pos_match = re.findall(
        r'(\d+\.\d+)\s*Dr',
        text
    )
    current_pos = "Not Found"
    if pos_match:
        current_pos = pos_match[-1]

    observation = f"""
Customer Name : {customer_name}
EMI Entries Found : {receipt_count}
Bounce Count : {bounce_count}
Bounce Charge Count : {bounce_charge_count}
Partial Payment Count : {partial_payment_count}
Current POS : ₹{current_pos}
FINAL OBSERVATION:

Customer repayment behaviour reviewed as per available SOA; EMI payment entries observed are {receipt_count}; total bounce count observed is {bounce_count}; bounce charge entries observed are {bounce_charge_count}; partial payment count observed is {partial_payment_count}; current POS observed is ₹{current_pos}.
"""
    st.text_area(
        "SOA Analysis",
        observation,
        height=400
    )

    st.subheader("SOA Text")

    st.text_area(
        "Extracted Data",
        text,
        height=400
    )
