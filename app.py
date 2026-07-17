import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="SOA Analyzer", layout="wide")

st.title("SOA Credit & DPD Analyzer")

uploaded_file = st.file_uploader(
    "Upload SOA PDF",
    type=["pdf"]
)

if uploaded_file:

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    st.success("PDF Read Successfully")

    # Customer Name
    customer = "Not Found"

    match = re.search(r'Ledger:\s*Mr\.\s*([^\n]+)', text)

    if match:
        customer = match.group(1).split("-")[0].strip()

    # Bounce Detection
    bounce_dates = []
    bounce_amounts = []

    bounce_pattern = r'(\d{2}-[A-Za-z]{3}-\d{2}).*?Bounced Return.*?(\d+\.\d+)'

    for m in re.finditer(bounce_pattern, text, re.DOTALL):
        bounce_dates.append(m.group(1))
        bounce_amounts.append(m.group(2))

    # Receipts
    receipt_pattern = r'(\d{2}-[A-Za-z]{3}-\d{2}).*?Receipt.*?(\d+\.\d+)'

    receipts = []

    for m in re.finditer(receipt_pattern, text):
        receipts.append(
            f"{m.group(1)} ₹{m.group(2)}"
        )

    # Behaviour
    if len(bounce_dates) == 0:
        behaviour = "Regular"
        reason = "No delinquency indication observed"
    else:
        behaviour = "Irregular"
        reason = "Insufficient funds / repayment irregularity"

    # Observation

    observation = f"""
Customer: {customer}

Credits Observed:
{chr(10).join(receipts[:10]) if receipts else "No Credits Found"}

No partial payment observed.

Bounce Count:
{len(bounce_dates)}

Bounce Details:
{chr(10).join([f"{d} ₹{a}" for d,a in zip(bounce_dates,bounce_amounts)]) if bounce_dates else "No Bounce Observed"}

Probable Reason:
{reason}

Repayment Behaviour:
{behaviour}
"""

    st.subheader("SOA Analysis")

    st.text_area(
        "Final Observation",
        observation,
        height=350
    )

    st.subheader("Extracted Text")

    st.text_area(
        "SOA Data",
        text,
        height=400
    )
