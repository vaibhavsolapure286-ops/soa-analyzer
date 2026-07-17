observation = f"""
Customer Name : {customer_name}
"""

EMI Entries Found : {receipt_count}

Bounce Count : {bounce_count}

Bounce Charge Count : {bounce_charge_count}

Partial Payment Count : {partial_payment_count}

Bulk Payment Count : {bulk_payment_count}

Cleared Bounce Count : {cleared_bounce_count}

Pending Bounce Count : {pending_bounce_count}

Current POS : ₹{current_pos}

Current Overdue : ₹{current_overdue}

Current DPD : {current_dpd_days} Days ({current_dpd_months} Months)

Maximum DPD : {max_dpd_days} Days ({max_dpd_months} Months)

Bounce Details :

{bounce_details_text}

FINAL OBSERVATION :

Customer paid EMI of ₹{emi_amount} from {first_payment_month} to {last_payment_month}; total bounce count observed is {bounce_count}; {bounce_observation}; cleared bounce count is {cleared_bounce_count} and pending bounce count is {pending_bounce_count}; partial payment count observed is {partial_payment_count}; bulk payment count observed is {bulk_payment_count}; current POS is ₹{current_pos}; current overdue amount is ₹{current_overdue}; current DPD is {current_dpd_days} days ({current_dpd_months} months); maximum DPD observed is {max_dpd_days} days ({max_dpd_months} months); overall repayment behaviour is assessed as {repayment_behaviour}.
"""

st.text_area(
    "SOA Analysis",
    observation,
    height=650
)
