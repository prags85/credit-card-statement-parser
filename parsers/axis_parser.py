"""
Axis Bank Credit Card Statement Parser
Handles Axis Bank specific PDF statement formats
"""

import re
from typing import Dict, List, Optional, Tuple
import pdfplumber
import pandas as pd
from parsers.base_parser import BaseCreditCardParser


class AxisParser(BaseCreditCardParser):
    """Parser for Axis Bank Credit Card Statements"""
    
    def __init__(self, pdf_path: str):
        super().__init__(pdf_path)
        self.bank_name = "Axis Bank"
    
    def extract_card_number(self, text: str) -> Optional[str]:
        """Extract last 4 digits of Axis card number"""
        patterns = [
            r'Card\s+Number\s*:?\s*(?:X+|\*+)?(\d{4})',
            r'(\d{4})\s*Axis'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_billing_cycle(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract Axis billing cycle dates"""
        patterns = [
            r'Statement\s+Period\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+to\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'From\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+To\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.standardize_date(match.group(1)), self.standardize_date(match.group(2))
        return None, None
    
    def extract_due_date(self, text: str) -> Optional[str]:
        """Extract Axis payment due date"""
        patterns = [
            r'Payment\s+Due\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Due\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.standardize_date(match.group(1))
        return None
    
    def extract_amount_due(self, text: str) -> Optional[float]:
        """Extract Axis total amount due"""
        patterns = [
            r'Total\s+Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'Amount\s+Payable\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.parse_indian_amount(match.group(1))
        return None
    
    def extract_transactions(self, pdf_path: str) -> List[Dict]:
        """Extract Axis transaction details"""
        transactions = []
        try:
            import tabula
            dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, stream=True)
            for df in dfs:
                for idx, row in df.iterrows():
                    row_str = ' '.join([str(x) for x in row.values if pd.notna(x)])
                    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', row_str)
                    amount_match = re.search(r'([\d,]+\.\d{2})', row_str)
                    if date_match and amount_match:
                        transactions.append({
                            'Date': self.standardize_date(date_match.group(1)),
                            'Description': row_str.strip(),
                            'Amount': self.parse_indian_amount(amount_match.group(1))
                        })
        except:
            pass
        return transactions
