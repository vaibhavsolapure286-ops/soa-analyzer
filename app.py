import streamlit as st
import pdfplumber

st.set_page_config(page_title="SOA Analyzer")

st.title("SOA PDF Analyzer")

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
                text += page_text

    st.success("PDF Read Successfully")

    st.subheader("Extracted Text")

    st.text_area(
        "SOA Data",
        text,
        height=400
    )
