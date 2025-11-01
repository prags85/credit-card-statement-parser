"""
Base Parser Class for Credit Card Statement Parsing
Provides abstract interface that all bank-specific parsers must implement
"""

from abc import ABC, abstractmethod
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd


class BaseCreditCardParser(ABC):
    """Abstract base class for credit card statement parsers"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extracted_data = {
            'card_last_4_digits': None,
            'billing_cycle_start': None,
            'billing_cycle_end': None,
            'payment_due_date': None,
            'total_amount_due': None,
            'transactions': []
        }
        self.bank_name = "Unknown"
        
    @abstractmethod
    def extract_card_number(self, text: str) -> Optional[str]:
        """Extract last 4 digits of card number"""
        pass
    
    @abstractmethod
    def extract_billing_cycle(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract billing cycle start and end dates"""
        pass
    
    @abstractmethod
    def extract_due_date(self, text: str) -> Optional[str]:
        """Extract payment due date"""
        pass
    
    @abstractmethod
    def extract_amount_due(self, text: str) -> Optional[float]:
        """Extract total amount due"""
        pass
    
    @abstractmethod
    def extract_transactions(self, pdf_path: str) -> List[Dict]:
        """Extract all transactions from statement"""
        pass
    
    def parse(self) -> Dict:
        """Main parsing method that orchestrates extraction"""
        import pdfplumber
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Extract text from all pages
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                
                # Extract all data points
                self.extracted_data['card_last_4_digits'] = self.extract_card_number(full_text)
                cycle_start, cycle_end = self.extract_billing_cycle(full_text)
                self.extracted_data['billing_cycle_start'] = cycle_start
                self.extracted_data['billing_cycle_end'] = cycle_end
                self.extracted_data['payment_due_date'] = self.extract_due_date(full_text)
                self.extracted_data['total_amount_due'] = self.extract_amount_due(full_text)
                self.extracted_data['transactions'] = self.extract_transactions(self.pdf_path)
                
            return {
                'success': True,
                'bank': self.bank_name,
                'data': self.extracted_data
            }
        except Exception as e:
            return {
                'success': False,
                'bank': self.bank_name,
                'error': str(e),
                'data': self.extracted_data
            }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert extracted data to pandas DataFrame"""
        if not self.extracted_data['transactions']:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.extracted_data['transactions'])
        
        # Add metadata columns
        df['Card_Last_4_Digits'] = self.extracted_data['card_last_4_digits']
        df['Billing_Cycle'] = f"{self.extracted_data['billing_cycle_start']} to {self.extracted_data['billing_cycle_end']}"
        df['Payment_Due_Date'] = self.extracted_data['payment_due_date']
        df['Total_Amount_Due'] = self.extracted_data['total_amount_due']
        df['Bank'] = self.bank_name
        
        return df
    
    @staticmethod
    def parse_indian_amount(amount_str: str) -> Optional[float]:
        """Parse Indian number format (with commas) to float"""
        if not amount_str:
            return None
        try:
            cleaned = re.sub(r'[₹$,\s]', '', str(amount_str))
            if '(' in cleaned and ')' in cleaned:
                cleaned = '-' + cleaned.replace('(', '').replace(')', '')
            return float(cleaned)
        except:
            return None
    
    @staticmethod
    def standardize_date(date_str: str) -> Optional[str]:
        """Convert various date formats to standard YYYY-MM-DD"""
        if not date_str:
            return None
        
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%d/%m/%y', '%d-%m-%y', '%d.%m.%y',
            '%d %b %Y', '%d %B %Y',
            '%d-%b-%Y', '%d-%B-%Y',
            '%Y-%m-%d'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except:
                continue
        return date_str
