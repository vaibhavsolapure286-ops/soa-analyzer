import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="SOA Analyzer", layout="wide")

st.title("SOA Analyzer")

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

    customer = "Not Found"

    cust_match = re.search(
        r"Mr\.\s+([A-Za-z\s]+)-\d+",
        text
    )

    if cust_match:
        customer = cust_match.group(1).strip()

    emi_match = re.findall(
        r"EMI received.*?(\d+\.\d+)",
        text,
        flags=re.IGNORECASE
    )

    emi_amount = emi_match[0] if emi_match else "Not Found"

    bounce_found = False
    bounce_date = ""

    bounce_pattern = r"(\d{2}-[A-Za-z]{3}-\d{2}).*?Bounced Return"

    bounce_search = re.search(
        bounce_pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if bounce_search:
        bounce_found = True
        bounce_date = bounce_search.group(1)

    bounce_charge = "No"

    if "EMI Bouncing Charges" in text:
        bounce_charge = "Yes"

    assessment = "Positive"
    remark = "Regular repayment behaviour observed."

    if bounce_found:
        assessment = "Mild Negative"
        remark = (
            "One isolated bounce observed. "
            "Account otherwise appears regular."
        )

    st.subheader("Analysis Result")

    st.write("Customer:", customer)
    st.write("EMI Amount:", emi_amount)
    st.write("Bounce Found:", "Yes" if bounce_found else "No")
    st.write("Bounce Charges:", bounce_charge)
    st.write("Assessment:", assessment)

    st.text_area(
        "Remark",
        remark,
        height=100
    )
