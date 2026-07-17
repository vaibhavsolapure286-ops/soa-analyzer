if pdf_file and excel_file:

    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    dpd_df = pd.read_excel(excel_file)

    customer_match = re.search(
        r'Ledger:\s*Mr\.\s*([^\n]+)',
        text
    )

    customer_name = "Not Found"

    if customer_match:
        customer_name = (
            customer_match
            .group(1)
            .split("-")[0]
            .strip()
        )

    match = dpd_df[
        dpd_df.astype(str)
        .apply(lambda x: x.str.contains(
            customer_name,
            case=False,
            na=False
        ))
        .any(axis=1)
    ]

    max_dpd = 0
    current_overdue = 0
    lan = "Not Available"

    if len(match) > 0:

        if "Loan No" in match.columns:
            lan = str(match.iloc[0]["Loan No"])

        if "Max DPD" in match.columns:
            max_dpd = match.iloc[0]["Max DPD"]

        if "Current Overdue" in match.columns:
            current_overdue = match.iloc[0]["Current Overdue"]

    emi_amount = None

    receipts = []
    partials = []
    bulk_payments = []
    bounces = []

    receipt_pattern = r'(\d{2}-[A-Za-z]{3}-\d{2}).*?Receipt.*?(\d+\.\d+)'

    for m in re.finditer(
        receipt_pattern,
        text
    ):
        receipts.append(
            (
                m.group(1),
                float(m.group(2))
            )
        )

    if receipts:
        emi_amount = receipts[0][1]

    for date, amt in receipts:

        if emi_amount:

            if amt < emi_amount:
                partials.append(
                    f"{date} ₹{amt:,.0f}"
                )

            if amt >= (emi_amount * 2):
                bulk_payments.append(
                    f"{date} ₹{amt:,.0f}"
                )

    lines = text.split("\n")

    for i, line in enumerate(lines):

        if (
            "Bounced Return" in line
            or "Bounce" in line
        ):

            date_match = re.search(
                r'(\d{2}-[A-Za-z]{3}-\d{2})',
                line
            )

            amount_match = re.search(
                r'(\d+\.\d+)',
                line
            )

            bounce_date = (
                date_match.group(1)
                if date_match else ""
            )

            bounce_amt = (
                amount_match.group(1)
                if amount_match else ""
            )

            bounces.append(
                (
                    bounce_date,
                    bounce_amt,
                    "Insufficient Funds"
                )
            )

    if current_overdue > 0:

        dpd_status = (
            "customer has not cleared the delinquency and overdue is still outstanding"
        )

    else:

        dpd_status = (
            "customer has cleared the delinquency and account is presently regular"
        )

    if len(bounces) == 0 and current_overdue == 0:

        behaviour = "Regular"

    elif len(bounces) <= 2 and current_overdue == 0:

        behaviour = "Average"

    else:

        behaviour = "Irregular"

    if len(bounces) > 0:

        reason = (
            "insufficient funds and irregular cash flow"
        )

    elif current_overdue > 0:

        reason = (
            "customer has not regularized overdue obligations"
        )

    else:

        reason = (
            "no delinquency observed"
        )

    credit_summary = (
        f"EMI of ₹{emi_amount:,.0f} received on "
        + ", ".join(
            [x[0] for x in receipts]
        )
        if emi_amount
        else "payments observed"
    )

    partial_summary = (
        ", ".join(partials)
        if partials
        else "no partial payment observed"
    )

    bulk_summary = (
        ", ".join(bulk_payments)
        if bulk_payments
        else "no bulk payment observed"
    )

    bounce_summary = (
        "; ".join(
            [
                f"{d} for ₹{float(a):,.0f} due to {r}"
                for d, a, r in bounces
                if a
            ]
        )
        if bounces
        else "no bounce observed"
    )

    final_observation = f"""
Customer credited {credit_summary}; {partial_summary}; {bulk_summary}; bounce observed on {bounce_summary}; current overdue amount ₹{current_overdue:,.0f}; Max DPD observed {max_dpd} days; {dpd_status}; probable reason for delinquency appears {reason}; repayment behaviour {behaviour}.
"""

    st.subheader("Analysis")

    st.write("Customer Name:", customer_name)
    st.write("LAN:", lan)
    st.write("Max DPD:", max_dpd)
    st.write("Current Overdue:", current_overdue)

    st.text_area(
        "Final Observation",
        final_observation,
        height=250
    )
