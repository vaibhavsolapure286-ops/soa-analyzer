import streamlit as st
import pdfplumber
import re
from datetime import datetime
from collections import defaultdict

st.title("SOA Analyzer")

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

    # ------------------------------
    # CUSTOMER NAME
    # ------------------------------

    customer_name = "Not Found"

    customer_match = re.search(
        r'Ledger:\s*Mr[s]?\.\s*([^\n]+)',
        text
    )

    if customer_match:
        customer_name = (
            customer_match.group(1)
            .split("-")[0]
            .strip()
        )

    # ------------------------------
    # EMI RECEIPTS
    # ------------------------------

    receipt_count = text.lower().count("receipt")

    # ------------------------------
    # BOUNCES
    # ------------------------------

    bounce_count = (
        text.lower().count("bounced return")
    )

    # ------------------------------
    # BOUNCE CHARGES
    # ------------------------------

    bounce_charge_count = (
        text.lower().count("emi bouncing charges")
    )

    # ------------------------------
    # PARTIAL PAYMENT
    # ------------------------------

    partial_payment_count = 0

    if "Pending" in text:
        partial_payment_count += 1

    # ------------------------------
    # CURRENT POS
    # ------------------------------

    pos_match = re.findall(
        r'(\d+\.\d+)\s*Dr',
        text
    )

    current_pos = "Not Found"

    if pos_match:
        current_pos = pos_match[-1]

    # ------------------------------
    # OVERDUE
    # ------------------------------

    current_overdue = "Check Bounce Recovery"

    # ------------------------------
    # DEBIT VS CREDIT ANALYSIS
    # ------------------------------

    # Pattern to extract transactions with dates, debit, and credit amounts
    # Adjust regex based on your SOA format
    transaction_pattern = r'(\d{2}-\w{3}-\d{4})\s+.*?(\d+\.?\d*)\s*(Cr|Dr)'
    
    monthly_data = defaultdict(lambda: {"debit": 0, "credit": 0, "transactions": []})
    
    matches = re.finditer(transaction_pattern, text, re.IGNORECASE)
    
    for match in matches:
        try:
            date_str = match.group(1)
            amount = float(match.group(2))
            transaction_type = match.group(3).upper()
            
            # Parse date and extract month-year
            try:
                date_obj = datetime.strptime(date_str, "%d-%b-%Y")
                month_key = date_obj.strftime("%b-%Y")
            except:
                month_key = date_str
            
            if transaction_type == "DR":
                monthly_data[month_key]["debit"] += amount
            else:  # CR
                monthly_data[month_key]["credit"] += amount
            
            monthly_data[month_key]["transactions"].append({
                "date": date_str,
                "amount": amount,
                "type": transaction_type
            })
        except:
            continue
    
    # Analyze debit vs credit by month
    debit_more_months = []
    credit_more_months = []
    
    for month, data in sorted(monthly_data.items()):
        if data["debit"] > data["credit"]:
            shortfall = data["debit"] - data["credit"]
            debit_more_months.append({
                "month": month,
                "debit": data["debit"],
                "credit": data["credit"],
                "shortfall": shortfall
            })
        elif data["credit"] > data["debit"]:
            excess = data["credit"] - data["debit"]
            credit_more_months.append({
                "month": month,
                "debit": data["debit"],
                "credit": data["credit"],
                "excess": excess
            })
shortfall_analysis = []

for month in sorted(monthly_debit.keys()):

    debit = monthly_debit.get(month, 0)
    credit = monthly_credit.get(month, 0)

    if debit > credit:

        shortfall = debit - credit

        recovered_month = "Not Recovered"
        recovered_amount = 0

        months_list = sorted(monthly_credit.keys())

        current_index = months_list.index(month) if month in months_list else -1

        if current_index >= 0:

            for next_month in months_list[current_index + 1:]:

                next_credit = monthly_credit.get(next_month, 0)
                next_debit = monthly_debit.get(next_month, 0)

                excess = max(0, next_credit - next_debit)

                if excess > 0:

                    recovered_month = next_month
                    recovered_amount = min(shortfall, excess)
                    break

        shortfall_analysis.append(
            f"""
Month : {month}
Debit Amount : ₹{debit:,.0f}
Credit Amount : ₹{credit:,.0f}
Shortfall Amount : ₹{shortfall:,.0f}
Recovered In : {recovered_month}
Recovered Amount : ₹{recovered_amount:,.0f}
"""
        )
shortfall_summary = (2    "\n".join(shortfall_analysis)3    
                     if shortfall_analysis4    else "No Shortfall Observed"5)6 7# Format debit > credit months with recovery info8debit_more_summary = ""
    if debit_more_months:
        debit_more_summary = "\nMonths where Debit > Credit (Shortfall):\n"
        for item in debit_more_months:
            debit_more_summary += f"  • {item['month']}: Debit: ₹{item['debit']:.2f}, Credit: ₹{item['credit']:.2f}, Shortfall: ₹{item['shortfall']:.2f}\n"
    else:
        debit_more_summary = "\nNo months with Debit > Credit.\n"
    
    # Format credit > debit months
    credit_more_summary = ""
    if credit_more_months:
        credit_more_summary = f"\nMonths where Credit > Debit ({len(credit_more_months)} months):\n"
        for item in credit_more_months:
            credit_more_summary += f"  • {item['month']}: Debit: ₹{item['debit']:.2f}, Credit: ₹{item['credit']:.2f}, Excess: ₹{item['excess']:.2f}\n"
    else:
        credit_more_summary = "\nNo months with Credit > Debit.\n"

    # ------------------------------
    # FINAL OBSERVATION
    # ------------------------------

    observation = f"""
Customer Name: {customer_name}

EMI Payments Observed: {receipt_count}

Bounce Count: {bounce_count}

Bounce Charge Entries: {bounce_charge_count}

Partial Payment Count: {partial_payment_count}

Current POS: ₹{current_pos}

Current Overdue: {current_overdue}

{debit_more_summary}

{credit_more_summary}

Final Observation:

Customer repayment behaviour reviewed as per available SOA; EMI payment entries observed are {receipt_count}; total bounce count observed is {bounce_count}; bounce charge entries observed are {bounce_charge_count}; partial payment count observed is {partial_payment_count}; current POS is ₹{current_pos}; current overdue requires verification against bounce recovery entries.

Debit vs Credit Analysis: 
- Months with shortfall (Debit > Credit): {len(debit_more_months)}
- Months with excess credit: {len(credit_more_months)}

Overall repayment behaviour should be assessed based on bounce regularisation, overdue clearance status, payment continuity and monthly debit-credit patterns.
"""

    st.text_area(
        "SOA Analysis",
        observation,
        height=500
    )

    # Display detailed breakdown
    st.subheader("Monthly Debit-Credit Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if debit_more_months:
            st.warning("⚠️ Months with Shortfall (Debit > Credit)")
            for item in debit_more_months:
                st.write(f"**{item['month']}**")
                st.write(f"  Debit: ₹{item['debit']:.2f}")
                st.write(f"  Credit: ₹{item['credit']:.2f}")
                st.write(f"  Shortfall: ₹{item['shortfall']:.2f}")
    
    with col2:
        if credit_more_months:
            st.info(f"ℹ️ Months with Excess Credit ({len(credit_more_months)} months)")
            for item in credit_more_months:
                st.write(f"**{item['month']}**")
                st.write(f"  Debit: ₹{item['debit']:.2f}")
                st.write(f"  Credit: ₹{item['credit']:.2f}")
                st.write(f"  Excess: ₹{item['excess']:.2f}")

    st.download_button(
        "Download Observation",
        observation,
        file_name="soa_observation.txt"
