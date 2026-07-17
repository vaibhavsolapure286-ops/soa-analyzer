bounce_details = []

for i, bounce in enumerate(bounces, start=1):
    bounce_details.append(
        f"""
{i}.
   Bounce Date      : {bounce['bounce_date']}
   Bounce Amount    : ₹{bounce['amount']}
   Cleared          : {bounce['cleared']}
   Cleared On       : {bounce['cleared_on']}
   Delay            : {bounce['delay']}
   Bounce Charges   : {bounce['charges_status']}
"""
    )
