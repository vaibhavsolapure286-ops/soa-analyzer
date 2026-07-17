prompt = f"""
...
FINAL OBSERVATION:

Customer paid EMI of ₹X from Month-Year to Month-Year; total bounce count observed is X; bounce observed on DD-MMM-YYYY for ₹X due to X reason; bounce was regularized on DD-MMM-YYYY through payment of ₹X with DPD of X days (X months); cleared bounce count is X and pending bounce count is X; partial payment count observed is X; bulk payment count observed is X; debit amount exceeded credit amount in X month(s) with total shortfall of ₹X, out of which ₹X was recovered in subsequent month(s); credit amount exceeded debit amount in X month(s); current POS is ₹X; current overdue amount is ₹X; current DPD is X days (X months); maximum DPD observed is X days (X months); penalty/bounce charge entries observed are X; customer has cleared/not cleared delinquent dues; overall repayment behaviour is assessed as Regular/Average/Irregular.

SOA DATA:

{text}
"""
