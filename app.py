SOA Review Summary# ----------------------------
# NEGATIVE REMARKS CHECK
# ----------------------------

negative_keywords = [
    "default",
    "settlement",
    "write off",
    "write-off",
    "legal",
    "recovery",
    "repossession",
    "sarfaesi",
    "auction"
]

negative_remarks = []

for keyword in negative_keywords:
    if keyword.lower() in text.lower():
        negative_remarks.append(keyword)

# ----------------------------
# EMI PAYMENT STATUS
# ----------------------------

if partial_payments:
    emi_status = (
        f"{len(partial_payments)} partial payment(s) observed"
    )
else:
    emi_status = (
        "all EMI payments appear fully paid as per available SOA"
    )

# ----------------------------
# OVERDUE STATUS
# ----------------------------

if current_overdue > 0:

    overdue_status = (
        f"outstanding overdue amount of ₹{current_overdue:,.0f} remains unpaid"
    )

else:

    overdue_status = (
        "no overdue amount is outstanding"
    )

# ----------------------------
# DPD STATUS
# ----------------------------

if current_dpd_days > 0:

    dpd_status = (
        f"current DPD estimated at {current_dpd_days} days ({current_dpd_months} months)"
    )

else:

    dpd_status = (
        "no current DPD observed"
    )

# ----------------------------
# BOUNCE STATUS
# ----------------------------

if bounce_count > 0:

    bounce_status = (
        f"total bounce count {bounce_count}, cleared bounce count {cleared_bounce_count} and pending bounce count {pending_bounce_count}"
    )

else:

    bounce_status = (
        "no cheque, ECS or NACH bounce observed"
    )

# ----------------------------
# NEGATIVE REMARK STATUS
# ----------------------------

if negative_remarks:

    negative_status = (
        "negative remarks observed: "
        + ", ".join(negative_remarks)
    )

else:

    negative_status = (
        "no negative remarks such as default, settlement, write-off, legal action or recovery proceedings observed"
    )

# ----------------------------
# FINAL OBSERVATION
# ----------------------------

final_observation = f"""
SOA Review Summary:

Customer Name: {customer_name}

EMI Review:
{emi_status}

Bounce Review:
{bounce_status}

Overdue Review:
{overdue_status}

DPD Review:
{dpd_status}

Negative Remarks:
{negative_status}

Overall Repayment Behaviour:

Customer repayment record reviewed based on the available SOA; {emi_status}; {bounce_status}; {overdue_status}; {dpd_status}; {negative_status}; overall repayment behaviour assessed as {behaviour}.
"""

Customer Name: Paras Rathore

EMI Review:
All EMI payments appear fully paid as per available SOA.

Bounce Review:
Total bounce count 4, cleared bounce count 3 and pending bounce count 1.

Overdue Review:
No overdue amount is outstanding.

DPD Review:
No current DPD observed.

Negative Remarks:
No negative remarks such as default, settlement, write-off, legal action or recovery proceedings observed.

Overall Repayment Behaviour:

Customer repayment record reviewed based on the available SOA; all EMI payments appear fully paid as per available SOA; total bounce count 4, cleared bounce count 3 and pending bounce count 1; no overdue amount is outstanding; no current DPD observed; no negative remarks such as default, settlement, write-off, legal action or recovery proceedings observed; overall repayment behaviour assessed as Irregular with historical bounce instances.
