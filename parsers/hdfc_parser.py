"""
HDFC Bank Credit Card Statement Parser
Handles HDFC Bank specific PDF statement formats
"""

import re
from typing import Dict, List, Optional, Tuple
import pdfplumber
import pandas as pd
from parsers.base_parser import BaseCreditCardParser


class HDFCParser(BaseCreditCardParser):
    """Parser for HDFC Bank Credit Card Statements"""
    
    def __init__(self, pdf_path: str):
        super().__init__(pdf_path)
        self.bank_name = "HDFC Bank"
    
    def extract_card_number(self, text: str) -> Optional[str]:
        """Extract last 4 digits of HDFC card number"""
        patterns = [
            r'Card\s+(?:Number|No\.?)\s*:?\s*(?:X+|\*+)?(\d{4})',
            r'(?:X{12}|\*{12})(\d{4})',
            r'Card\s+ending\s+(?:with|in)\s+(\d{4})',
            r'(\d{4})\s+HDFC'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_billing_cycle(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract HDFC billing cycle dates"""
        patterns = [
            r'Statement\s+(?:Period|Date|from)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:to|-|till)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Billing\s+Cycle\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:to|-|till)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'From\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:to|To)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_date = self.standardize_date(match.group(1))
                end_date = self.standardize_date(match.group(2))
                return start_date, end_date
        return None, None
    
    def extract_due_date(self, text: str) -> Optional[str]:
        """Extract HDFC payment due date"""
        patterns = [
            r'Payment\s+Due\s+(?:Date|By)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Due\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Pay\s+By\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.standardize_date(match.group(1))
        return None
    
    def extract_amount_due(self, text: str) -> Optional[float]:
        """Extract HDFC total amount due"""
        patterns = [
            r'Total\s+Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'New\s+Balance\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'Current\s+Outstanding\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.parse_indian_amount(match.group(1))
        return None
    
    def extract_transactions(self, pdf_path: str) -> List[Dict]:
        """Extract HDFC transaction details"""
        transactions = []
        
        try:
            import tabula
            dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, stream=True, guess=False)
            
            for df in dfs:
                if df.empty or len(df.columns) < 3:
                    continue
                
                for idx, row in df.iterrows():
                    row_str = ' '.join([str(x) for x in row.values if pd.notna(x)])
                    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', row_str)
                    amount_match = re.search(r'([\d,]+\.\d{2})', row_str)
                    
                    if date_match and amount_match:
                        transaction = {
                            'Date': self.standardize_date(date_match.group(1)),
                            'Description': row_str.strip(),
                            'Amount': self.parse_indian_amount(amount_match.group(1))
                        }
                        transactions.append(transaction)
        
        except Exception:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        for table in tables:
                            if not table:
                                continue
                            
                            for row in table[1:]:
                                if len(row) >= 3:
                                    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', str(row[0]))
                                    if date_match:
                                        transaction = {
                                            'Date': self.standardize_date(date_match.group(0)),
                                            'Description': str(row[1]) if len(row) > 1 else '',
                                            'Amount': self.parse_indian_amount(str(row[-1]))
                                        }
                                        transactions.append(transaction)
            except:
                pass
        
        return transactions
