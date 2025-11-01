"""
Credit Card Statement Parser - Main Entry Point
Supports: HDFC, ICICI, SBI, Axis, Kotak Bank Credit Cards
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

# Import all parsers (ensure parsers folder is in your PYTHONPATH)
from parsers.hdfc_parser import HDFCParser
from parsers.icici_parser import ICICIParser
from parsers.sbi_parser import SBIParser
from parsers.axis_parser import AxisParser
from parsers.kotak_parser import KotakParser


class CreditCardStatementProcessor:
    """Main processor for credit card statements"""

    def __init__(self, input_dir='input', output_dir='output'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Bank detection keywords mapped to parser classes
        self.bank_keywords = {
            'hdfc': HDFCParser,
            'icici': ICICIParser,
            'sbi': SBIParser,
            'axis': AxisParser,
            'kotak': KotakParser
        }

    def detect_bank(self, pdf_path: str) -> str:
        """Detect bank from PDF content"""
        import pdfplumber

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Check first 2 pages
                text = ""
                for page in pdf.pages[:2]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text.lower()

                # Detect bank based on keywords
                if 'hdfc' in text:
                    return 'hdfc'
                elif 'icici' in text:
                    return 'icici'
                elif 'sbi card' in text or 'sbi credit' in text:
                    return 'sbi'
                elif 'axis' in text:
                    return 'axis'
                elif 'kotak' in text:
                    return 'kotak'
        except Exception as e:
            print(f"Error detecting bank: {e}")

        return 'unknown'

    def process_single_statement(self, pdf_path: str) -> dict:
        """Process a single credit card statement"""
        print(f"\nProcessing: {pdf_path}")

        # Detect bank
        bank = self.detect_bank(pdf_path)
        print(f"Detected bank: {bank.upper()}")

        if bank == 'unknown':
            return {
                'success': False,
                'file': str(pdf_path),
                'error': 'Could not detect bank from statement'
            }

        # Get appropriate parser
        parser_class = self.bank_keywords.get(bank)
        if not parser_class:
            return {
                'success': False,
                'file': str(pdf_path),
                'error': f'No parser available for {bank}'
            }

        # Parse statement
        try:
            parser = parser_class(str(pdf_path))
            result = parser.parse()

            if result['success']:
                # Save to CSV
                df = parser.to_dataframe()
                if not df.empty:
                    output_file = self.output_dir / f"{Path(pdf_path).stem}_{bank}_extracted.csv"
                    df.to_csv(output_file, index=False)
                    result['output_csv'] = str(output_file)
                    print(f"✓ Extracted {len(df)} transactions")
                    print(f"✓ Saved to: {output_file}")

                # Print summary
                print(f"\nExtracted Data Summary:")
                print(f"  Card Last 4 Digits: {result['data']['card_last_4_digits']}")
                print(f"  Billing Cycle: {result['data']['billing_cycle_start']} to {result['data']['billing_cycle_end']}")
                print(f"  Payment Due Date: {result['data']['payment_due_date']}")
                print(f"  Total Amount Due: ₹{result['data']['total_amount_due']}")
                print(f"  Transactions Found: {len(result['data']['transactions'])}")
            else:
                print(f"✗ Parsing failed: {result.get('error', 'Unknown error')}")

            result['file'] = str(pdf_path)
            return result

        except Exception as e:
            return {
                'success': False,
                'file': str(pdf_path),
                'error': str(e)
            }

    def process_all_statements(self):
        """Process all PDF statements in input directory"""
        pdf_files = list(self.input_dir.glob('*.pdf')) + list(self.input_dir.glob('*.PDF'))

        if not pdf_files:
            print(f"No PDF files found in {self.input_dir}")
            return

        print(f"Found {len(pdf_files)} PDF statement(s)\n")
        print("=" * 80)

        results = []
        for pdf_file in pdf_files:
            result = self.process_single_statement(str(pdf_file))
            results.append(result)
            print("=" * 80)

        # Generate summary report
        self.generate_summary_report(results)

    def generate_summary_report(self, results: list):
        """Generate summary report of all processed statements"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"processing_report_{timestamp}.json"

        summary = {
            'timestamp': timestamp,
            'total_processed': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'details': results
        }

        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n{'='*80}")
        print("PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Total Statements Processed: {summary['total_processed']}")
        print(f"Successfully Parsed: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"\nDetailed report saved to: {report_file}")
        print(f"{'='*80}\n")


def parse_credit_card_statement(pdf_file) -> dict:
    """
    Function to parse a single credit card PDF file-like object.
    Used in Streamlit UI or anywhere else needing single file parsing.
    """
    import tempfile

    # Write uploaded file-like object to temp file for parser (it needs a file path)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name

    processor = CreditCardStatementProcessor(input_dir='', output_dir='output')
    result = processor.process_single_statement(tmp_path)

    # Clean up temp file
    os.remove(tmp_path)

    return result


def main():
    """Main entry point"""
    print("=" * 80)
    print("CREDIT CARD STATEMENT PARSER")
    print("Supports: HDFC, ICICI, SBI, Axis, Kotak Bank")
    print("=" * 80)

    processor = CreditCardStatementProcessor(
        input_dir='input',
        output_dir='output'
    )

    processor.process_all_statements()


if __name__ == "__main__":
    main()
