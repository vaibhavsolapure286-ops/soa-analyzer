import streamlit as st
import pdfplumber

st.set_page_config(page_title="SOA Credit Analyzer")

st.title("SOA Credit Analyzer")

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

    st.subheader("SOA Review Prompt")

    review_prompt = f"""
You are a Credit Risk Analyst.

Review the following Statement of Account (SOA) and provide a detailed repayment behaviour assessment.

Rules:

1. Verify whether EMI payments were paid regularly.
2. Identify all EMI payment dates and amounts.
3. Check for any missed EMI.
4. Check for any delayed EMI.
5. Check for any partial EMI payment and mention:
   - Date
   - Month
   - Amount
6. Check for any bulk EMI payment and mention:
   - Date
   - Month
   - Amount
7. Check for cheque, ECS or NACH bounce entries.
8. For every bounce mention:
   - Bounce Date
   - Bounce Month
   - Bounce Amount
   - Bounce Reason
9. Verify whether the bounced EMI was subsequently cleared.
10. If cleared, mention:
    - Recovery Date
    - Recovery Month
    - Recovery Amount
    - DPD Days
    - DPD Months
11. Count:
    - Total Bounce Count
    - Cleared Bounce Count
    - Pending Bounce Count
12. Verify bounce charges, late payment charges, penalty charges, overdue charges and penal interest.
13. Mention all charges with:
    - Date
    - Amount
14. Calculate:
    - Current Overdue Amount
    - Current DPD in Days
    - Current DPD in Months
    - Maximum DPD in Days
    - Maximum DPD in Months
15. If DPD Days = 147 then show:
    Maximum DPD = 147 Days (4.9 Months)
16. Verify whether the customer has completely cleared all delinquent dues.
17. If customer has not cleared dues:
    - Mention pending amount
    - Mention probable reason
18. Check for negative remarks:
    - Default
    - Settlement
    - Write-Off
    - Legal Action
    - Recovery Proceedings
    - SARFAESI
    - Repossession
19. Mention whether any negative remark exists.
20. Assess repayment behaviour:
    - Regular
    - Average
    - Irregular

Give output in exactly this format:

Customer Name:

EMI Amount:

EMI Review:

Bounce Review:

Partial Payment Review:

Bulk Payment Review:

Penalty Charges Review:

Current Overdue:

Current DPD:

Maximum DPD:

Negative Remarks:

Final Observation:

Customer paid EMI of ₹X from Month-Year to Month-Year; total bounce count observed is X; bounce observed on DD-MMM-YYYY (Month-Year) for ₹X due to insufficient funds; bounce was regularized on DD-MMM-YYYY through payment of ₹X with DPD of X days (X months); cleared bounce count is X and pending bounce count is X; partial payment count observed is X; bulk payment count observed is X; current overdue amount is ₹X; current DPD is X days (X months); maximum DPD observed is X days (X months); penalty charge entries observed are X; no/negative remarks observed; customer has cleared/not cleared all delinquent dues; probable reason for delinquency appears X; overall repayment behaviour is assessed as Regular/Average/Irregular.

SOA DATA:

{text}
"""

    st.text_area(
        "Copy this prompt into AI",
        review_prompt,
        height=600
    )
