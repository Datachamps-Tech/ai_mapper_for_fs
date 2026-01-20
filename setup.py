"""
Setup script for AI Accounting Mapper
Creates sample training data and initializes the project
"""

import pandas as pd
from pathlib import Path
import config

def create_sample_training_data():
    """Create sample training data Excel file"""
    
    # Sample data with common accounting line items
    sample_data = {
        'primary_group': [
            # Balance Sheet items
            'Cash in Hand',
            'Cash at Bank',
            'Sundry Debtors',
            'Accounts Receivable',
            'Inventory',
            'Stock in Trade',
            'Land and Building',
            'Plant and Machinery',
            'Furniture and Fixtures',
            'Vehicles',
            'Goodwill',
            'Computer Software',
            'Sundry Creditors',
            'Accounts Payable',
            'Bank Overdraft',
            'Short Term Loan',
            'Long Term Loan',
            'Capital Account',
            'Reserves and Surplus',
            'Accumulated Depreciation',
            'TDS Payable',
            'GST Payable',
            'Input GST Credit',
            'PF Payable',
            'ESIC Payable',
            'Advance to Suppliers',
            'Advance from Customers',
            'Prepaid Insurance',
            'Prepaid Rent',
            'Outstanding Expenses',
            'Accrued Income',
            
            # Profit & Loss items
            'Sales Revenue',
            'Service Revenue',
            'Sales Returns',
            'Purchases',
            'Purchase Returns',
            'Salaries and Wages',
            'Rent Expense',
            'Electricity Charges',
            'Telephone Expenses',
            'Internet Charges',
            'Office Supplies',
            'Printing and Stationery',
            'Advertising Expenses',
            'Marketing Expenses',
            'Social Media Advertising',
            'Google Ads',
            'Insurance Premium',
            'Repairs and Maintenance',
            'Professional Fees',
            'Legal Fees',
            'Audit Fees',
            'Bank Charges',
            'Interest on Loan',
            'Interest Income',
            'Discount Allowed',
            'Discount Received',
            'Bad Debts',
            'Depreciation Expense',
            'Conveyance Expenses',
            'Travel Expenses',
            'Commission Paid',
            'Commission Received',
        ],
        'fs': [
            # Balance Sheet
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            'Balance Sheet', 'Balance Sheet', 'Balance Sheet',
            
            # Profit & Loss
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
            'Profit & Loss', 'Profit & Loss', 'Profit & Loss', 'Profit & Loss',
        ]
    }
    
    # Create DataFrame with all columns
    df = pd.DataFrame(sample_data)
    
    # Add empty columns for other fields
    for col in config.ALL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    
    # Reorder columns
    df = df[config.ALL_COLUMNS]
    
    # Save to Excel
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_excel(config.TRAINING_EXCEL, index=False)
    
    print(f"✅ Created sample training data: {config.TRAINING_EXCEL}")
    print(f"   Total rows: {len(df)}")
    print(f"   Balance Sheet: {len(df[df['fs'] == 'Balance Sheet'])}")
    print(f"   Profit & Loss: {len(df[df['fs'] == 'Profit & Loss'])}")
    
    return df


def setup_project():
    """Initialize project structure"""
    
    print("🚀 Setting up AI Accounting Mapper...")
    print()
    
    # Create directories
    dirs = [
        config.DATA_DIR,
        config.INPUT_DIR,
        config.OUTPUT_DIR,
        config.BATCH_OUTPUT_DIR,
        config.SINGLE_OUTPUT_DIR
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    print()
    
    # Create sample training data if not exists
    if not config.TRAINING_EXCEL.exists():
        create_sample_training_data()
    else:
        print(f"ℹ️  Training data already exists: {config.TRAINING_EXCEL}")
    
    print()
    print("✨ Setup complete!")
    print()
    print("Next steps:")
    print("1. Edit data/training_data.xlsx to add your own accounting line items")
    print("2. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print("3. Run: streamlit run app.py")
    print()


if __name__ == "__main__":
    setup_project()
