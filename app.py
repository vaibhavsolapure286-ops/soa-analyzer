prompt = f"""
Review the Statement of Account (SOA) and provide repayment observations.

SOA Data:

Credits:
{credits}

Bounces:
{bounces}

Current Overdue:
{overdue}

Maximum DPD:
{dpd}

Please verify and report:

1. Whether EMI payments were paid regularly and on time.
2. Any delayed, missed, or irregular EMI payments.
3. Any partial payment made by the customer:
   - Date
   - Month
   - Amount Paid
   - Pending Amount

4. Any bulk payment made by the customer:
   - Date
   - Month
   - Amount

5. Any Cheque/ECS/NACH bounce:
   - Bounce Date
   - Bounce Month
   - Bounce Amount
   - Bounce Reason
   - Bounce Charges Applied

6. Whether the bounced EMI was subsequently cleared:
   - Recovery Date
   - Recovery Month
   - Recovery Amount
   - DPD Days
   - DPD Months

7. Calculate:
   - Total Bounce Count
   - Cleared Bounce Count
   - Pending Bounce Count

8. Verify:
   - Current Overdue Amount
   - Whether customer has cleared overdue or not

9. Calculate:
   - Current DPD in Days
   - Current DPD in Months
   - Maximum DPD in Days
   - Maximum DPD in Months

10. Convert DPD into months:
    Example:
    147 Days = 4.9 Months

11. Check for:
   - Bounce Charges
   - Penalty Charges
   - Late Payment Charges
   - Overdue Charges
   - Penal Interest

12. Check for negative remarks:
   - Default
   - Settlement
   - Write-Off
   - Legal Action
   - Recovery Proceedings
   - Repossession

13. Mention Current POS / Closing Outstanding Balance.

Generate the final output in ONE SENTENCE ONLY in the following format:

Customer paid EMI of ₹[EMI Amount] from [First EMI Month-Year] to [Last EMI Month-Year]; total bounce count observed is [Bounce Count]; bounce observed on [Bounce Date] ([Bounce Month]) for ₹[Bounce Amount] due to [Bounce Reason]; bounce was regularized on [Recovery Date] through payment of ₹[Recovery Amount] with DPD of [DPD Days] days ([DPD Months] months); cleared bounce count is [Cleared Bounce Count] and pending bounce count is [Pending Bounce Count]; partial payment count observed is [Partial Payment Count]; bulk payment count observed is [Bulk Payment Count]; current POS is ₹[POS Amount]; current overdue amount is ₹[Overdue Amount]; current DPD is [Current DPD Days] days ([Current DPD Months] months); maximum DPD observed is [Maximum DPD Days] days ([Maximum DPD Months] months); penalty/bounce charge entries observed are [Penalty Count]; no/adverse remarks observed; customer has cleared/not cleared all delinquent dues; probable reason for delinquency appears [Reason]; overall repayment behaviour is assessed as Regular/Average/Irregular.
"""
