prompt = f"""
Review the Statement of Account (SOA) and provide repayment observations.

1. Verify whether EMI payments were paid regularly and on time.

2. Mention delayed, missed, or irregular EMI payments.

3. Identify partial payments:
- Date
- Month
- Amount Paid
- Pending Amount

4. Identify bulk payments:
- Date
- Month
- Amount
- Number of EMIs covered

5. Identify all Cheque/ECS/NACH bounces:
- Bounce Date
- Bounce Month
- Bounce Amount
- Bounce Reason
- Bounce Charges Applied

6. For every bounced EMI:
- Check whether it was subsequently cleared
- Recovery Date
- Recovery Month
- Recovery Amount
- DPD in Days
- DPD in Months

7. Calculate:
- Total Bounce Count
- Cleared Bounce Count
- Pending Bounce Count

8. Current Status:
- Current POS
- Current Overdue Amount
- Current DPD in Days
- Current DPD in Months
- Maximum DPD in Days
- Maximum DPD in Months

9. Month-wise Debit vs Credit Analysis

A. Identify months where Debit Amount is greater than Credit Amount.

For each month provide:
- Month
- Total Debit Amount
- Total Credit Amount
- Shortfall Amount

B. Verify whether the shortfall amount was recovered later.

Mention:
- Recovery Month
- Recovery Amount
- Whether Fully Recovered or Partially Recovered

C. Identify months where Credit Amount is greater than Debit Amount.

For each month provide:
- Month
- Total Debit Amount
- Total Credit Amount
- Excess Credit Amount

D. Mention:
- Total months where Debit exceeded Credit
- Total months where Credit exceeded Debit
- Total Shortfall Amount
- Total Shortfall Recovered

10. Check for:
- Bounce Charges
- Penalty Charges
- Overdue Charges
- Penal Interest
- Late Payment Charges

11. Check for negative remarks:
- Default
- Settlement
- Write-Off
- Legal Action
- Recovery Proceedings
- SARFAESI
- Repossession

Output Format:

Customer Name:

EMI Review:

Bounce Review:

Month-wise Debit vs Credit Analysis:

Months Where Debit > Credit:

Month:
Debit:
Credit:
Shortfall:
Recovered In:
Recovery Amount:
Status:

Months Where Credit > Debit:

Month:
Debit:
Credit:
Excess Credit:

Current POS:

Current Overdue:

Current DPD:

Maximum DPD:

Negative Remarks:

FINAL OBSERVATION:

Customer paid EMI of ₹X from Month-Year to Month-Year; total bounce count observed is X; bounce observed on DD-MMM-YYYY for ₹X due to X reason; bounce was regularized on DD-MMM-YYYY through payment of ₹X with DPD of X days (X months); cleared bounce count is X and pending bounce count is X; partial payment count observed is X; bulk payment count observed is X; debit amount exceeded credit amount in X month(s) with total shortfall of ₹X, out of which ₹X was recovered in subsequent month(s); credit amount exceeded debit amount in X month(s); current POS is ₹X; current overdue amount is ₹X; current DPD is X days (X months); maximum DPD observed is X days (X months); penalty/bounce charge entries observed are X; customer has cleared/not cleared delinquent dues; overall repayment behaviour is assessed as Regular/Average/Irregular.

SOA DATA:

{text}
"""
