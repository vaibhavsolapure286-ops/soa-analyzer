import streamlit as st
import pdfplumber
import pandas as pd
import openpyx1
import re

st.set_page_config(page_title="SOA Analyzer")

st.title("SOA + DPD Analyzer")

pdf_file = st.file_uploader(
    "Upload SOA PDF",
    type=["pdf"]
)

excel_file = st.file_uploader(
    "Upload DPD Excel",
    type=["xlsx"]
)

if pdf_file and excel_file:

    # Read PDF
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Read Excel
    df = pd.read_excel(excel_file)

    # Customer Name
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

    # Match Excel using Customer Name

    match = df[
        df.astype(str)
        .apply(
            lambda x: x.str.contains(
                customer_name,
                case=False,
                na=False
            )
        )
        .any(axis=1)
    ]

    max_dpd = 0
    overdue = 0
    loan_no = ""

    if len(match) > 0:

        if "Loan No" in match.columns:
            loan_no = str(match.iloc[0]["Loan No"])

        if "Max DPD" in match.columns:
            max_dpd = match.iloc[0]["Max DPD"]

        if "Current Overdue" in match.columns:
            overdue = match.iloc[0]["Current Overdue"]

    # Bounce Detection

    bounce_lines = []

    for line in text.split("\n"):

        if (
            "Bounced Return" in line
            or "Bounce" in line
            or "insufficient fund" in line.lower()
        ):
            bounce_lines.append(line)

    bounce_count = len(bounce_lines)

    # Behaviour

    if bounce_count == 0 and overdue == 0:
        behaviour = "Regular"

    elif bounce_count > 0 and overdue == 0:
        behaviour = "Average"

    else:
        behaviour = "Irregular"

    # DPD Status

    if overdue > 0:

        dpd_status = (
            "customer has not cleared the delinquency and overdue is still outstanding"
        )

    else:

        dpd_status = (
            "customer has cleared the delinquency and account is presently regular"
        )

    # Reason

    if bounce_count > 0:
        reason = (
            "insufficient funds and irregular cash flow"
        )

    elif overdue > 0:
        reason = (
            "non regularization of overdue obligations"
        )

    else:
        reason = (
            "no delinquency observed"
        )

    # Final Observation

    observation = f"""
Customer Name : {customer_name}

Loan Number : {loan_no}

Max DPD : {max_dpd}

Current Overdue : ₹{overdue}

Final Observation:

Customer account reviewed from SOA and DPD records; total bounce instances observed {bounce_count}; current overdue amount ₹{overdue}; Max DPD observed {max_dpd} days; {dpd_status}; probable reason for delinquency appears {reason}; repayment behaviour {behaviour}.
"""

    st.subheader("Analysis")

    st.text_area(
        "Result",
        observation,
        height=300
    )
