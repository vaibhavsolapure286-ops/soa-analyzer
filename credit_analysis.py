"""
Customer Credit/EMI Payment Analysis System
Analyzes debit (EMI paid), credit (EMI due), and payment patterns
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class CustomerCreditAnalysis:
    """Analyzes customer EMI payment patterns and credit metrics"""
    
    def __init__(self, customer_data: Dict):
        """
        Initialize with customer data
        
        Args:
            customer_data: Dict with keys:
                - customer_name
                - emi_amount
                - total_due
                - total_paid
                - outstanding
                - max_dpd
                - pending_emi_count
                - transactions: List of transaction records with date, type, amount
        """
        self.customer_data = customer_data
        self.transactions_df = None
        self.monthly_analysis = None
        
    def load_transactions(self, transactions: List[Dict]) -> pd.DataFrame:
        """
        Load and process transaction data
        
        Args:
            transactions: List of dicts with 'date', 'type' (Debit/Credit), 'amount'
        
        Returns:
            DataFrame with processed transactions
        """
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        df['amount'] = pd.to_numeric(df['amount'])
        self.transactions_df = df
        return df
    
    def monthly_debit_credit_analysis(self) -> pd.DataFrame:
        """
        Analyze monthly debit vs credit amounts
        
        Returns:
            DataFrame with monthly debit, credit, and variance analysis
        """
        if self.transactions_df is None:
            raise ValueError("No transactions loaded. Call load_transactions() first.")
        
        # Group by month and transaction type
        monthly = self.transactions_df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        
        # Ensure both columns exist
        if 'Debit' not in monthly.columns:
            monthly['Debit'] = 0
        if 'Credit' not in monthly.columns:
            monthly['Credit'] = 0
        
        # Calculate variance and comparison
        monthly['Difference'] = monthly['Debit'] - monthly['Credit']
        monthly['Status'] = monthly['Difference'].apply(
            lambda x: 'Debit > Credit' if x > 0 else ('Debit < Credit' if x < 0 else 'Balanced')
        )
        
        self.monthly_analysis = monthly
        return monthly.reset_index()
    
    def months_debit_greater_than_credit(self) -> pd.DataFrame:
        """
        Find months where Debit amount > Credit amount
        
        Returns:
            DataFrame of months with debit > credit
        """
        if self.monthly_analysis is None:
            self.monthly_debit_credit_analysis()
        
        result = self.monthly_analysis[self.monthly_analysis['Difference'] > 0].copy()
        return result.reset_index(drop=True)
    
    def months_debit_less_than_credit(self) -> pd.DataFrame:
        """
        Find months where Debit amount < Credit amount (Shortfall months)
        
        Returns:
            DataFrame of shortfall months with details
        """
        if self.monthly_analysis is None:
            self.monthly_debit_credit_analysis()
        
        result = self.monthly_analysis[self.monthly_analysis['Difference'] < 0].copy()
        result['Shortfall_Amount'] = abs(result['Difference'])
        return result.reset_index(drop=True)
    
    def get_customer_summary(self) -> Dict:
        """
        Generate customer credit assessment summary
        
        Returns:
            Dictionary with key metrics and assessment
        """
        data = self.customer_data
        
        # Calculate metrics
        payment_percentage = (data['total_paid'] / data['total_due'] * 100) if data['total_due'] > 0 else 0
        outstanding_percentage = (data['outstanding'] / data['total_due'] * 100) if data['total_due'] > 0 else 0
        
        # Determine risk level
        if data['max_dpd'] > 90:
            risk_level = "HIGH RISK"
        elif data['max_dpd'] > 60:
            risk_level = "MEDIUM RISK"
        elif data['max_dpd'] > 30:
            risk_level = "LOW-MEDIUM RISK"
        else:
            risk_level = "LOW RISK"
        
        summary = {
            'customer_name': data['customer_name'],
            'emi_amount': f"₹{data['emi_amount']:,.2f}",
            'total_due': f"₹{data['total_due']:,.2f}",
            'total_paid': f"₹{data['total_paid']:,.2f}",
            'outstanding': f"₹{data['outstanding']:,.2f}",
            'payment_percentage': f"{payment_percentage:.2f}%",
            'outstanding_percentage': f"{outstanding_percentage:.2f}%",
            'max_dpd': data['max_dpd'],
            'pending_emi_count': data['pending_emi_count'],
            'risk_level': risk_level,
            'assessment': data['assessment']
        }
        
        return summary
    
    def generate_report(self) -> str:
        """
        Generate comprehensive analysis report
        
        Returns:
            Formatted report string
        """
        summary = self.get_customer_summary()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CUSTOMER CREDIT ANALYSIS REPORT                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 CUSTOMER INFORMATION:
{'─' * 80}
Customer Name:          {summary['customer_name']}
Assessment:             {summary['assessment'].upper()}
Risk Level:             {summary['risk_level']}

💰 FINANCIAL SUMMARY:
{'─' * 80}
EMI Amount:             {summary['emi_amount']}
Total Due:              {summary['total_due']}
Total Paid:             {summary['total_paid']} ({summary['payment_percentage']})
Outstanding:            {summary['outstanding']} ({summary['outstanding_percentage']})

⏰ PAYMENT STATUS:
{'─' * 80}
Maximum DPD:            {summary['max_dpd']} days
Pending EMI Count:      {summary['pending_emi_count']}

"""
        
        # Monthly Analysis
        if self.monthly_analysis is not None:
            debit_gt_credit = self.months_debit_greater_than_credit()
            debit_lt_credit = self.months_debit_less_than_credit()
            
            report += f"""
📊 MONTHLY ANALYSIS:
{'─' * 80}

🔴 MONTHS WHERE DEBIT > CREDIT (Positive Payment):
{'' if len(debit_gt_credit) > 0 else '   None'}
"""
            
            if len(debit_gt_credit) > 0:
                for idx, row in debit_gt_credit.iterrows():
                    report += f"""   Month:      {row['month']}
   Debit:      ₹{row['Debit']:,.2f}
   Credit:     ₹{row['Credit']:,.2f}
   Difference: ₹{row['Difference']:,.2f}
{'─' * 80}
"""
            
            report += f"""
🟡 MONTHS WHERE DEBIT < CREDIT (Shortfall):
Count: {len(debit_lt_credit)} months
{'' if len(debit_lt_credit) > 0 else '   None'}
"""
            
            if len(debit_lt_credit) > 0:
                for idx, row in debit_lt_credit.iterrows():
                    report += f"""   Month:      {row['month']}
   Debit:      ₹{row['Debit']:,.2f}
   Credit:     ₹{row['Credit']:,.2f}
   Shortfall:  ₹{row['Shortfall_Amount']:,.2f}
{'─' * 80}
"""
        
        report += f"""
📝 REMARKS:
{'─' * 80}
• Outstanding liability of {summary['outstanding']} remains unpaid
• Maximum delinquency observed is {summary['max_dpd']} DPD
• Repayment conduct indicates stress
• {summary['pending_emi_count']} EMI payments are pending

"""
        
        return report
    
    def export_to_json(self, filename: str = 'customer_analysis.json'):
        """Export analysis results to JSON file"""
        export_data = {
            'customer_summary': self.get_customer_summary(),
            'monthly_analysis': self.monthly_analysis.to_dict('records') if self.monthly_analysis is not None else None,
            'months_debit_gt_credit': self.months_debit_greater_than_credit().to_dict('records'),
            'months_debit_lt_credit': self.months_debit_less_than_credit().to_dict('records')
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return f"Report exported to {filename}"


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    # Sample customer data
    customer_info = {
        'customer_name': 'XYZ',
        'emi_amount': 15790,
        'total_due': 378960,
        'total_paid': 355270,
        'outstanding': 23690,
        'max_dpd': 37,
        'pending_emi_count': 2,
        'assessment': 'Negative'
    }
    
    # Sample transaction data (24 months)
    transactions = [
        # Month 1
        {'date': '2024-01-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-01-15', 'type': 'Debit', 'amount': 14500},
        
        # Month 2
        {'date': '2024-02-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-02-20', 'type': 'Debit', 'amount': 15790},
        
        # Month 3
        {'date': '2024-03-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-03-10', 'type': 'Debit', 'amount': 16000},
        
        # Month 4 (Shortfall)
        {'date': '2024-04-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-04-25', 'type': 'Debit', 'amount': 8000},
        
        # Month 5
        {'date': '2024-05-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-05-12', 'type': 'Debit', 'amount': 15790},
        
        # Month 6 (Shortfall)
        {'date': '2024-06-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-06-30', 'type': 'Debit', 'amount': 10000},
        
        # Month 7
        {'date': '2024-07-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-07-08', 'type': 'Debit', 'amount': 17500},
        
        # Month 8
        {'date': '2024-08-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-08-15', 'type': 'Debit', 'amount': 15790},
        
        # Month 9 (Shortfall)
        {'date': '2024-09-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-09-20', 'type': 'Debit', 'amount': 5000},
        
        # Month 10
        {'date': '2024-10-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-10-10', 'type': 'Debit', 'amount': 16200},
        
        # Month 11
        {'date': '2024-11-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-11-18', 'type': 'Debit', 'amount': 15790},
        
        # Month 12
        {'date': '2024-12-05', 'type': 'Credit', 'amount': 15790},
        {'date': '2024-12-22', 'type': 'Debit', 'amount': 14800},
    ]
    
    # Create analyzer instance
    analyzer = CustomerCreditAnalysis(customer_info)
    
    # Load transactions
    analyzer.load_transactions(transactions)
    
    # Perform monthly analysis
    monthly_df = analyzer.monthly_debit_credit_analysis()
    
    print("\n" + "="*80)
    print("MONTHLY DEBIT vs CREDIT ANALYSIS")
    print("="*80)
    print(monthly_df.to_string(index=False))
    
    # Get months where debit > credit
    print("\n" + "="*80)
    print("MONTHS WHERE DEBIT > CREDIT:")
    print("="*80)
    debit_gt = analyzer.months_debit_greater_than_credit()
    if len(debit_gt) > 0:
        print(debit_gt[['month', 'Debit', 'Credit', 'Difference']].to_string(index=False))
        print(f"\nTotal Months: {len(debit_gt)}")
    else:
        print("No months found where Debit > Credit")
    
    # Get months where debit < credit (Shortfall)
    print("\n" + "="*80)
    print("MONTHS WHERE DEBIT < CREDIT (SHORTFALL MONTHS):")
    print("="*80)
    debit_lt = analyzer.months_debit_less_than_credit()
    if len(debit_lt) > 0:
        print(debit_lt[['month', 'Debit', 'Credit', 'Shortfall_Amount']].to_string(index=False))
        print(f"\nTotal Shortfall Months: {len(debit_lt)}")
        print(f"Total Shortfall Amount: ₹{debit_lt['Shortfall_Amount'].sum():,.2f}")
    else:
        print("No shortfall months found")
    
    # Generate full report
    print("\n")
    report = analyzer.generate_report()
    print(report)
    
    # Export to JSON
    # analyzer.export_to_json()
