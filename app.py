import streamlit as st
import pdfplumber
import re
from datetime import datetime

st.set_page_config(page_title="SOA Credit Assessment Tool")

st.title("SOA Credit Assessment Tool")

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

    # ==========================
    # CUSTOMER NAME
    # ==========================

    customer = "Not Found"

    m = re.search(
        r"Mr\.\s+([A-Za-z\s]+)-\d+",
        text
    )

    if m:
        customer = m.group(1).strip()

    # ==========================
    # EMI AMOUNT
    # ==========================

    emi_amount = 0

    emi_match = re.findall(
        r"EMI.*?(\d{4,6}\.?\d*)",
        text,
        re.IGNORECASE
    )

    if emi_match:
        try:
            emi_amount = float(emi_match[0])
        except:
            emi_amount = 0

    # ==========================
    # BOUNCE DETECTION
    # ==========================

    bounce_found = False
    bounce_date = ""
    bounce_amount = 0

    bounce_pattern = re.search(
        r"(\d{2}-[A-Za-z]{3}-\d{2}).*?Bounced Return.*?(\d{4,6}\.?\d*)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if bounce_pattern:
        bounce_found = True

        bounce_date = bounce_pattern.group(1)

        try:
            bounce_amount = float(
                bounce_pattern.group(2)
            )
        except:
            bounce_amount = emi_amount

    # ==========================
    # BOUNCE CHARGES
    # ==========================

    bounce_charges = 0

    charge_match = re.search(
        r"EMI Bouncing Charges.*?(\d+\.\d+)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if charge_match:
        try:
            bounce_charges = float(
                charge_match.group(1)
            )
        except:
            pass

    # ==========================
    # RECOVERY DETECTION
    # ==========================

    recovery_found = False
    recovery_date = ""

    if bounce_found:

        receipt_dates = re.findall(
            r"(\d{2}-[A-Za-z]{3}-\d{2}).*?Receipt.*?15790",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if receipt_dates:

            for d in receipt_dates:

                if d != bounce_date:
                    recovery_found = True
                    recovery_date = d
                    break

    # ==========================
    # DELAY DAYS
    # ==========================

    delay_days = 0

    if bounce_found and recovery_found:

        try:
            d1 = datetime.strptime(
                bounce_date,
                "%d-%b-%y"
            )

            d2 = datetime.strptime(
                recovery_date,
                "%d-%b-%y"
            )

            delay_days = (
                d2 - d1
            ).days

        except:
            pass

    # ==========================
    # OUTSTANDING
    # ==========================

    outstanding_amount = 0

    if bounce_found and not recovery_found:
        outstanding_amount = bounce_amount

    # ==========================
    # ASSESSMENT
    # ==========================

    assessment = "Positive"

    if bounce_found and recovery_found:
        assessment = "Mild Negative"

    elif bounce_found and not recovery_found:
        assessment = "Negative"

    # ==========================
    # REMARK
    # ==========================

    if assessment == "Positive":

        remark = (
            "Regular repayment behaviour observed. "
            "No bounce, overdue liability or carry-forward amount detected."
        )

    elif assessment == "Mild Negative":

        remark = (
            f"EMI bounce observed on {bounce_date}. "
            f"Recovered on {recovery_date}. "
            f"Delay of {delay_days} day(s) noted. "
            "Repayment behaviour indicates temporary stress but subsequent recovery was observed."
        )

    else:

        remark = (
            f"Bounced EMI of ₹{bounce_amount:,.0f} remains unpaid. "
            "No corresponding recovery transaction identified. "
            "Liability appears carried forward and repayment stress is evident."
        )

    # ==========================
    # DISPLAY
    # ==========================

    st.header("SOA Assessment")

    st.write("### Customer Name")
    st.write(customer)

    st.write("### EMI Amount")
    st.write(
        f"₹{emi_amount:,.0f}"
        if emi_amount
        else "Not Detected"
    )

    st.write("### Bounce Found")
    st.write("Yes" if bounce_found else "No")

    st.write("### Bounce Date")
    st.write(bounce_date or "NA")

    st.write("### Recovery Date")
    st.write(recovery_date or "Not Found")

    st.write("### Delay Days")
    st.write(delay_days)

    st.write("### Outstanding Amount")
    st.write(
        f"₹{outstanding_amount:,.0f}"
    )

    st.write("### Bounce Charges")
    st.write(
        f"₹{bounce_charges:,.0f}"
        if bounce_charges
        else "NA"
    )

    st.write("### Carry Forward")
    st.write(
        "Yes"
        if outstanding_amount > 0
        else "No"
    )

    st.write("### Assessment")
    st.success(assessment)

    st.write("### Remark")
    st.text_area(
        "",
        remark,
        height=150
    )
