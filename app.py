from datetime import datetime

EMI_DUE_DAY = 8

late_emi_details = []
max_dpd_days = 0

for receipt in receipts:

    try:

        payment_date = datetime.strptime(
            receipt["date"],
            "%d-%b-%y"
        )

        due_date = payment_date.replace(
            day=EMI_DUE_DAY
        )

        dpd_days = (
            payment_date - due_date
        ).days

        dpd_months = round(
            dpd_days / 30,
            1
        )

        if dpd_days > 0:

            same_month = (
                payment_date.month ==
                due_date.month
            )

            payment_status = (
                "Same Month"
                if same_month
                else "Next Month"
            )

            late_emi_details.append(
                f"""
EMI Due Date : {due_date.strftime('%d-%b-%Y')}
Payment Date : {payment_date.strftime('%d-%b-%Y')}
Delay : {dpd_days} Days ({dpd_months} Months)
Recovered In : {payment_status}
"""
            )

            max_dpd_days = max(
                max_dpd_days,
                dpd_days
            )

    except:
        pass

max_dpd_months = round(
    max_dpd_days / 30,
    1
)
