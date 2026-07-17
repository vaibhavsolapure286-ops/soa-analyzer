prompt = f"""
Review the following SOA.

SOA Data:

{text}

Check:

1. EMI paid regularly or not
2. Bounce count
3. Bounce dates
4. Bounce amount
5. Bounce cleared or not
6. Recovery date if cleared
7. Partial payments
8. Bulk payments
9. Current overdue
10. Current DPD
11. Maximum DPD
12. Current POS
13. Penalty charges
14. Negative remarks

Generate one final observation sentence.
"""
