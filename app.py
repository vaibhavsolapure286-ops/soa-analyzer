cleared_bounce_count = 0
pending_bounce_count = 0

bounce_details = []

for bounce in bounces:

    recovered = False

    bounce_date = datetime.strptime(
        bounce["date"],
        "%d-%b-%y"
    )

    for r in receipts:

        receipt_date = datetime.strptime(
            r["date"],
            "%d-%b-%y"
        )

        if receipt_date > bounce_date:

            dpd_days = (
                receipt_date -
                bounce_date
            ).days

            dpd_months = round(
                dpd_days / 30,
                1
            )

            cleared_bounce_count += 1

            recovered = True

            bounce_details.append(
                f"""
Bounce Date : {bounce['date']}
Bounce Amount : ₹{bounce['amount']:,.0f}
Recovered On : {r['date']}
Recovery Amount : ₹{r['amount']:,.0f}
DPD : {dpd_days} Days ({dpd_months} Months)
Status : Cleared
"""
            )

            break

    if not recovered:

        pending_bounce_count += 1

        bounce_details.append(
            f"""
Bounce Date : {bounce['date']}
Bounce Amount : ₹{bounce['amount']:,.0f}
Status : Pending
"""
        )
