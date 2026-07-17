prompt = f"""
Review this Statement of Account (SOA).

Provide only the following:

1. EMI Amount.

2. Total Bounce Count.

3. For each bounce:
   - Bounce Date
   - Bounce Amount
   - Bounce Reason
   - Was bounce recovered? (Yes/No)
   - Recovery Date
   - Recovery Amount
   - Was recovery done in same month or next month?
   - DPD Days = Recovery Date - Bounce Date

4. If bounce is not recovered:
   - Pending Amount
   - Current DPD Days = Today - Bounce Date

5. Identify any partial payment:
   - Date
   - Amount
   - Pending Balance

6. Mention:
   - Cleared Bounce Count
   - Pending Bounce Count

7. Final Observation in one sentence.

Output Format:

Bounce Review:

Bounce Date:
Bounce Amount:
Recovery Date:
Recovery Amount:
Recovered In:
DPD Days:

Partial Payment Review:

Cleared Bounce Count:

Pending Bounce Count:

Final Observation:

Customer paid EMI of ₹X; total bounce count observed is X; bounce dated DD-MMM-YYYY for ₹X was recovered on DD-MMM-YYYY in same month/next month with DPD of X days; partial payment of ₹X observed on DD-MMM-YYYY; cleared bounce count is X and pending bounce count is X; overall repayment behaviour is Regular/Average/Irregular.

SOA DATA:

{text}
"""
