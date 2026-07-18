import streamlit as st
import pdfplumber
import re

st.set_page_config(
    page_title="SOA Underwriting Analyzer",
    layout="wide"
)

st.title("SOA Underwriting Analyzer")

uploaded_file = st.file_uploader(
    "Upload SOA PDF",
    type=["pdf"]
)

if uploaded_file:

    text = ""

    try:

        with pdfplumber.open(uploaded_file) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        customer = "Not Found"

        match = re.search(
            r"Mr\.\s+([A-Za-z\s]+)-\d+",
            text
        )

        if match:
            customer = match.group(1).strip()

        emi_amount = 0

        emi_match = re.findall(
            r"EMI.*?(\d{4,6}\.?\d*)",
            text,
            flags=re.IGNORECASE
        )

        if emi_match:

            try:
                emi_amount = float(
                    emi_match[0]
                )

            except:
                pass

        bounce_found = False
        bounce_date = ""

        if "Bounced Return" in text:

            bounce_found = True

            date_match = re.search(
                r"(\d{2}-[A-Za-z]{3}-\d{2}).*?Bounced Return",
                text,
                re.IGNORECASE | re.DOTALL
            )

            if date_match:
                bounce_date = date_match.group(1)

        bounce_charges = 0

        charge_match = re.search(
            r"EMI Bouncing Charges.*?(\d+\.\d+)",
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if charge_match:

            try:
                bounce_charges = float(
                    charge_match.group(1)
                )
            except:
                pass

        if bounce_found:

            assessment = "Mild Negative"

            remark = (
                "EMI bounce observed. "
                "Customer repayment behaviour shows temporary stress. "
                "Recommend checking whether EMI was subsequently recovered."
            )

        else:

            assessment = "Positive"

            remark = (
                "Regular EMI repayment behaviour observed. "
                "No bounce transaction detected."
            )

        st.header("SOA Analysis")

        st.write("### Customer Name")
        st.write(customer)

        st.write("### EMI Amount")
        if emi_amount:
            st.write(f"₹{emi_amount:,.0f}")
        else:
            st.write("Not Detected")

        st.write("### Bounce Found")
        st.write("Yes" if bounce_found else "No")

        st.write("### Bounce Date")
        st.write(bounce_date if bounce_date else "NA")

        st.write("### Bounce Charges")
        if bounce_charges:
            st.write(f"₹{bounce_charges:,.0f}")
        else:
            st.write("NA")

        st.write("### Assessment")
        st.success(assessment)

        st.write("### Underwriting Remark")
        st.text_area(
            "",
            remark,
            height=120
        )

        with st.expander("View Extracted Text"):

            st.text_area(
                "SOA Data",
                text[:10000],
                height=400
            )

    except Exception as e:

        st.error(str(e))
