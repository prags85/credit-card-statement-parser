import streamlit as st
import pandas as pd
from io import BytesIO

# Import your parser main function that takes a PDF file-like object
# and returns extracted data as a dict with keys:
# 'bank', 'card_last_4', 'billing_cycle', 'due_date', 'total_due', 'transactions'
from main import parse_credit_card_statement

st.title("Credit Card Statement Parser")

uploaded_file = st.file_uploader("Upload your credit card statement (PDF)", type="pdf")

if uploaded_file is not None:
    with st.spinner("Parsing PDF..."):
        result = parse_credit_card_statement(uploaded_file)

    if result and result.get('success'):
        st.subheader("Extracted Information")
        st.write(f"Detected Bank: {result.get('data', {}).get('bank', 'Unknown')}")
        st.write(f"Card Last 4 Digits: {result.get('data', {}).get('card_last_4_digits', 'N/A')}")
        billing_cycle_start = result.get('data', {}).get('billing_cycle_start', '')
        billing_cycle_end = result.get('data', {}).get('billing_cycle_end', '')
        st.write(f"Billing Cycle: {billing_cycle_start} to {billing_cycle_end}")
        st.write(f"Payment Due Date: {result.get('data', {}).get('payment_due_date', 'N/A')}")
        st.write(f"Total Amount Due: {result.get('data', {}).get('total_amount_due', 'N/A')}")

        st.subheader("Transaction Details")
        transactions = result.get('data', {}).get('transactions')

        if transactions is not None:
            df = pd.DataFrame(transactions)
            st.dataframe(df)

            # Prepare CSV for download
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()

            st.download_button(
                label="Download Transactions as CSV",
                data=csv_data,
                file_name="transactions.csv",
                mime="text/csv"
            )
        else:
            st.write("No transactions found.")
    else:
        st.error(f"Failed to parse the statement: {result.get('error', 'Unknown error occurred.')}")
