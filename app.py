import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SOA Underwriting Analyzer")

st.title("SOA Underwriting Analyzer")

def calculate_profile(emi_schedule):

    total_due = 0
    total_paid = 0
    total_outstanding = 0

    pending_emi_count = 0
    max_dpd = 0

    emi_results = []

    for emi in emi_schedule:

        due_date = datetime.strptime(
            emi["due_date"],
            "%Y-%m-%d"
        )

        emi_amount = emi["emi_amount"]

        total_due += emi_amount

        paid_total = sum(
            p["amount"]
            for p in emi["payments"]
        )

        total_paid += paid_total

        outstanding = max(
            0,
            emi_amount - paid_total
        )

        total_outstanding += outstanding

        status = "Paid On Time"

        dpd = 0

        final_payment_date = None

        running_total = 0

        sorted_payments = sorted(
            emi["payments"],
            key=lambda x: x["date"]
        )

        for p in sorted_payments:

            running_total += p["amount"]

            if running_total >= emi_amount:

                final_payment_date = datetime.strptime(
                    p["date"],
                    "%Y-%m-%d"
                )

                break

        if outstanding > 0:

            status = "Unpaid"

            pending_emi_count += 1

            dpd = (
                datetime.today() - due_date
            ).days

        else:

            dpd = max(
                0,
                (final_payment_date - due_date).days
            )

            if dpd > 0:
                status = "Delayed"

        max_dpd = max(
            max_dpd,
            dpd
        )

        emi_results.append({
            "due_date": emi["due_date"],
            "emi_amount": emi_amount,
            "paid_amount": paid_total,
            "outstanding": outstanding,
            "dpd": dpd,
            "status": status
        })

    profile = "Positive"

    if pending_emi_count >= 2:
        profile = "High Risk"

    elif total_outstanding > 0:
        profile = "Negative"

    elif max_dpd > 30:
        profile = "Negative"

    elif max_dpd > 5:
        profile = "Mild Negative"

    if profile == "Positive":

        remark = (
            "EMIs serviced regularly. "
            "No outstanding liability observed."
        )

    elif profile == "Mild Negative":

        remark = (
            f"Maximum DPD observed is {max_dpd} days. "
            "All dues appear regularized."
        )

    elif profile == "Negative":

        remark = (
            f"Outstanding liability of ₹{total_outstanding:,.0f} remains unpaid. "
            f"Maximum DPD observed is {max_dpd} days."
        )

    else:

        remark = (
            f"{pending_emi_count} EMI(s) remain overdue. "
            f"Outstanding liability of ₹{total_outstanding:,.0f} is pending."
        )

    summary = {
        "Total EMI Due": total_due,
        "Total EMI Paid": total_paid,
        "Outstanding Amount": total_outstanding,
        "Pending EMI Count": pending_emi_count,
        "Maximum DPD": max_dpd,
        "Profile": profile,
        "Remark": remark
    }

    return emi_results, summary


sample_data = [
    {
        "due_date": "2025-01-08",
        "emi_amount": 15790,
        "payments": [
            {
                "date": "2025-01-20",
                "amount": 15790
            }
        ]
    }
]

if st.button("Run Sample Analysis"):

    results, summary = calculate_profile(sample_data)

    st.subheader("Summary")

    for k, v in summary.items():
        st.write(f"{k}: {v}")

    st.subheader("EMI Details")

    st.json(results)
