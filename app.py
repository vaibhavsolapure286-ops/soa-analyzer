import streamlit as st
import pdfplumber

st.title("SOA Analyzer")

pdf = st.file_uploader("Upload SOA PDF", type="pdf")

if pdf:
    text = ""

    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            text += page.extract_text()

    st.text_area("Extracted Text", text, height=300)
