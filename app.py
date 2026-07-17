import streamlit as st
import pdfplumber

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

    prompt = f"""
Review the Statement of Account (SOA) and provide repayment observations.

Check:

1. Whether EMI payments were paid regularly and on time.
2. Mention delayed or missed EMI payments.
3. Check for partial payments:
   - Date
   - Month
   - Amount
   - Pending Amount

4. Check for bulk payments:
   - Date
   - Month
   - Amount

5. Check all Cheque / ECS / NACH bounces:
   - Bounce Date
   - Bounce Month
   - Bounce Amount
   - Bounce Reason
   - Bounce Charges

6. If bounce is cleared:
   - Recovery Date
   - Recovery Month
   - Recovery Amount
   - DPD Days
   - DPD Months

7. Calculate:
   - Total Bounce Count
   - Cleared Bounce Count
   - Pending Bounce Count

8. Check overdue:
   - Current Overdue Amount
   - Whether customer cleared it

9. Calculate:
   - Current DPD Days
   - Current DPD Months
   - Maximum DPD Days
   - Maximum DPD Months

10. Convert DPD:
Example:
147 days = 4.9 months

11. Check:
   - Bounce Charges
   - Penal Charges
   - Late Payment Charges
   - Overdue Charges

12. Check:
   - Default
   - Settlement
   - Write-Off
   - Recovery Proceedings
   - Legal Action
   - Repossession

13. Mention Current POS from SOA.

Provide final observation in ONE SENTENCE ONLY.

Format:

Customer paid EMI of ₹X from Month-Year to Month-Year; total bounce count observed is X; bounce observed on DD-MMM-YYYY (Month-Year) for ₹X due to X reason; bounce was cleared on DD-MMM-YYYY through payment of ₹X with DPD of X days (X months); cleared bounce count is X and pending bounce count is X; partial payment count observed is X; bulk payment count observed is X; current POS is ₹X; current overdue amount is ₹X; current DPD is X days (X months); maximum DPD observed is X days (X months); penalty/bounce charge entries observed are X; no/adverse remarks observed; customer has cleared/not cleared delinquent dues; overall repayment behaviour is Regular/Average/Irregular.

SOA:

{text}
"""

    st.subheader("SOA Extracted")

    st.text_area(
        "SOA Text",
        text,
        height=300
    )

    st.subheader("Copy Below Prompt Into AI")

    st.text_area(
        "Analysis Prompt",
        prompt,
        height=600
    )
