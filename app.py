from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted
from reportlab.lib.styles import getSampleStyleSheet

styles=getSampleStyleSheet()
doc=SimpleDocTemplate("/mnt/data/SOA_Analyzer_Code_Starter.pdf")
story=[Paragraph("SOA Analyzer - Starter Code",styles["Heading1"]),
Paragraph("Below is the starter app.py structure. The full project is too large for a single PDF generated here, but this provides the foundation.",styles["BodyText"])]
code="""import streamlit as st
import pdfplumber
import re

st.title("SOA Analyzer")

uploaded_files = st.file_uploader(
    "Upload SOA PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for pdf_file in uploaded_files:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\\n"

        customer = re.search(r"Ledger:\\s*Mr[s]?\\.\\s*([^\\n]+)", text)
        customer_name = customer.group(1).split("-")[0].strip() if customer else "Not Found"

        bounce_count = text.lower().count("bounced return")
        bounce_charge_count = text.lower().count("emi bouncing charges")
        emi_count = text.lower().count("receipt")

        st.subheader(customer_name)
        st.write("EMI Count:", emi_count)
        st.write("Bounce Count:", bounce_count)
        st.write("Bounce Charges:", bounce_charge_count)

        # TODO:
        # Extract transaction rows
        # Match bounce -> recovery date
        # Calculate delay
        # Monthly debit vs credit
        # Shortfall calculation
        # DPD detection
        # Generate underwriting observation
"""
story.append(Preformatted(code, styles["Code"]))
doc.build(story)
print("/mnt/data/SOA_Analyzer_Code_Starter.pdf")
