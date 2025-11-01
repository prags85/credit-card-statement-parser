# Credit Card Statement Parser - Setup & Usage Guide

## 📥 Files You Have

1. **parsers/__init__.py** - Package initialization
2. **parsers/base_parser.py** - Abstract base class
3. **parsers/hdfc_parser.py** - HDFC Bank parser
4. **parsers/icici_parser.py** - ICICI Bank parser
5. **parsers/sbi_parser.py** - SBI Card parser
6. **parsers/axis_parser.py** - Axis Bank parser
7. **parsers/kotak_parser.py** - Kotak Bank parser
8. **main.py** - Main entry point
9. **requirements.txt** - Python dependencies

## 🚀 Quick Setup

### Step 1: Create Project Structure
```bash
mkdir credit_card_parser
cd credit_card_parser

# Create subdirectories
mkdir parsers
mkdir input
mkdir output
```

### Step 2: Place Python Files
- Place all `*_parser.py` files in the `parsers/` folder
- Place `main.py` in the root folder
- Place `requirements.txt` in the root folder

**Final structure:**
```
credit_card_parser/
├── main.py
├── requirements.txt
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py
│   ├── hdfc_parser.py
│   ├── icici_parser.py
│   ├── sbi_parser.py
│   ├── axis_parser.py
│   └── kotak_parser.py
├── input/          (for PDF statements)
└── output/         (for extracted data)
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Add PDF Statements
Place your credit card statement PDFs in the `input/` folder.

### Step 5: Run the Parser
```bash
python main.py
```

### Step 6: View Results
Check the `output/` folder for:
- **CSV files** - Extracted transactions with all 5 data points
- **JSON report** - Summary of processing

## 📊 What Gets Extracted

For each PDF statement, the parser extracts:

1. **Card Last 4 Digits** - e.g., "5678"
2. **Billing Cycle Period** - e.g., "2024-01-05 to 2024-02-04"
3. **Payment Due Date** - e.g., "2024-02-20"
4. **Total Amount Due** - e.g., "45230.50"
5. **Transaction Details** - Complete table with:
   - Transaction Date
   - Description/Merchant Name
   - Amount

## 🏦 Supported Banks

✅ HDFC Bank Credit Cards
✅ ICICI Bank Credit Cards
✅ SBI Card
✅ Axis Bank Credit Cards
✅ Kotak Mahindra Bank Credit Cards

## 📈 Output Example

### CSV File (hdfc_statement_hdfc_extracted.csv)
```
Date,Description,Amount,Card_Last_4_Digits,Billing_Cycle,Payment_Due_Date,Total_Amount_Due,Bank
2024-01-06,SWIGGY,450.00,5678,2024-01-05 to 2024-02-04,2024-02-20,45230.50,HDFC Bank
2024-01-08,AMAZON,1250.00,5678,2024-01-05 to 2024-02-04,2024-02-20,45230.50,HDFC Bank
```

### JSON Report (processing_report_*.json)
```json
{
  "timestamp": "20251101_213045",
  "total_processed": 1,
  "successful": 1,
  "failed": 0,
  "details": [
    {
      "success": true,
      "bank": "HDFC Bank",
      "file": "input/hdfc_statement.pdf",
      "output_csv": "output/hdfc_statement_hdfc_extracted.csv",
      "data": {
        "card_last_4_digits": "5678",
        "billing_cycle_start": "2024-01-05",
        "billing_cycle_end": "2024-02-04",
        "payment_due_date": "2024-02-20",
        "total_amount_due": 45230.50,
        "transactions": [...]
      }
    }
  ]
}
```

## ⚠️ Important Notes

1. **Password-Protected PDFs**
   - Most bank statements are password-protected
   - The password is usually: First 4 letters of name + DOB in DDMMYY format
   - To handle this, uncomment the password parameter in base_parser.py

2. **Text-Based PDFs Only**
   - Works best with text-based PDFs
   - Scanned/image-based PDFs require OCR

3. **Data Privacy**
   - Never share actual statements
   - Use your own or test/anonymized data

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'parsers'"
**Solution:** Make sure you're running from the project root and the folder structure is correct.

### Issue: "No transactions extracted"
**Solution:** 
- Check if PDF is text-based (not scanned)
- Verify it's from a supported bank
- Check if password protection is needed

### Issue: "Could not detect bank"
**Solution:**
- Make sure the PDF is from a supported bank
- Check if the bank name appears clearly in the first 2 pages

## ✅ Verification Checklist

- [ ] All 9 Python files are in place
- [ ] Folder structure is correct (parsers/ subfolder)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] input/ and output/ folders exist
- [ ] PDF statements placed in input/ folder
- [ ] main.py runs without errors
- [ ] CSV and JSON files generated in output/

## 🎯 Ready to Go!

Once setup is complete, your credit card statement parser is ready for:
- Processing individual statements
- Batch processing multiple statements
- Extracting all 5 required data points
- Generating professional CSV and JSON reports

For any issues, check the console output and detailed JSON report!
