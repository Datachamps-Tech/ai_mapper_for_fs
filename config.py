"""
Configuration file for AI Accounting Mapper
Contains all thresholds, settings, and domain-specific rules
"""

import os
from pathlib import Path

# ==================== PROJECT PATHS ====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
BATCH_OUTPUT_DIR = OUTPUT_DIR / "batch_predictions"
SINGLE_OUTPUT_DIR = OUTPUT_DIR / "single_predictions"

# Training data files
#TRAINING_EXCEL = DATA_DIR / "training_data.xlsx"
##TRAINING_CSV = DATA_DIR / "training_data.csv"
##TRAINING_JSON = DATA_DIR / "training_data.json"
##TRAINING_EMBEDDINGS = DATA_DIR / "training_embeddings.pkl"
##PROGRESS_CHECKPOINT = DATA_DIR / "progress.json"

# ==================== MATCHING THRESHOLDS ====================
THRESHOLDS = {
    'exact': 1.0,           # Exact match always 1.0
    'fuzzy': 0.85,          # Fuzzy match threshold
    'semantic': 0.85,       # spaCy semantic similarity
    'embeddings': 0.80,     # Sentence transformers
    'review': 0.70          # Below this = needs review
}

# ==================== MODEL CONFIGURATIONS ====================
SPACY_MODEL = "en_core_web_md"
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
OPENAI_MODEL = "gpt-5-nano"

# ==================== LLM SETTINGS ====================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MAX_RETRIES = 3
LLM_RETRY_DELAY = 2  # seconds, will use exponential backoff

# ==================== BATCH PROCESSING ====================
CHECKPOINT_INTERVAL = 10  # Save progress every N rows

# ==================== UI COLOR SCHEME ====================
COLORS = {
    'primary_blue': '#2E5090',
    'secondary_blue': '#4A90E2',
    'bg_light': '#F5F7FA',
    'success_green': '#28A745',
    'warning_amber': '#FFC107',
    'danger_red': '#DC3545'
}

# ==================== COMPANY DOMAINS ====================
COMPANY_DOMAINS = [
    "General Business",
    "SaaS / IT Services",
    "Manufacturing",
    "Retail / E-commerce",
    "Services / Consulting"
]

# ==================== DOMAIN-SPECIFIC RULES ====================
def get_domain_rules(domain: str) -> str:
    """Generate domain-specific classification rules for LLM prompt"""
    
    base_rules = """
===== SPECIFIC RULES =====

NOMINAL ACCOUNTS (Always → Profit & Loss):
- All Expenses: Salaries, Wages, Rent, Utilities, Insurance, Repairs, Advertising
- All Incomes: Sales, Service Revenue, Interest Income, Commission Income
- All Losses: Loss on Sale of Assets, Foreign Exchange Loss
- All Gains: Profit on Sale of Assets, Foreign Exchange Gain
- Purchases of Goods (for resale, not assets)
- Discounts (Given/Received)

REAL ACCOUNTS (Always → Balance Sheet):
- Tangible Assets: Land, Building, Plant & Machinery, Furniture, Vehicles, Cash, Inventory
- Intangible Assets: Goodwill, Patents, Trademarks, Software
- Accumulated Depreciation (contra asset)
- Investments (long-term or short-term)

PERSONAL ACCOUNTS (Always → Balance Sheet):
- Debtors / Accounts Receivable / Sundry Debtors
- Creditors / Accounts Payable / Sundry Creditors
- Bank Accounts (all types)
- Loans (Taken or Given)
- Capital Account
- Drawings Account
"""
    
    domain_specific = {
        "SaaS / IT Services": """
SAAS/IT SPECIFIC:
- Software Licenses (purchased) → Balance Sheet (Asset)
- Software Development Costs (capitalized) → Balance Sheet
- Cloud Hosting Costs → Profit & Loss (Expense)
- AWS/Azure/GCP Bills → Profit & Loss (Expense)
- SaaS Subscriptions (tools used) → Profit & Loss (Expense)
- Customer Subscriptions Revenue → Profit & Loss (Income)
- Domain & SSL Costs → Profit & Loss (Expense)
""",
        "Manufacturing": """
MANUFACTURING SPECIFIC:
- Raw Materials Inventory → Balance Sheet (Current Asset)
- Work in Progress (WIP) → Balance Sheet (Current Asset)
- Finished Goods Inventory → Balance Sheet (Current Asset)
- Factory Rent → Profit & Loss → Direct Expense
- Direct Labor → Profit & Loss → Direct Expense 
- Indirect Labor → Profit & Loss (Manufacturing Overhead)
- Machinery Purchase → Balance Sheet (Fixed Asset)
- Machinery Repairs → Profit & Loss (Expense)
""",
        "Retail / E-commerce": """
RETAIL/E-COMMERCE SPECIFIC:
- Inventory/Stock → Balance Sheet (Current Asset)
- Payment Gateway Charges → Profit & Loss (Expense)
- Shipping & Logistics → Profit & Loss (Expense)
- Packaging Costs → Profit & Loss (Expense)
- E-commerce Platform Fees → Profit & Loss (Expense)
- Returns & Refunds → Profit & Loss (Contra Revenue)
- Store Fixtures → Balance Sheet (Fixed Asset)
""",
        "Services / Consulting": """
SERVICES/CONSULTING SPECIFIC:
- Professional Fees Revenue → Profit & Loss (Income)
- Consultant Payments → Profit & Loss (Expense)
- Project Advances Received → Balance Sheet (Current Liability)
- Unbilled Revenue → Balance Sheet (Current Asset)
- Deferred Revenue → Balance Sheet (Current Liability)
- Office Supplies → Profit & Loss (Expense)
""",
        "General Business": """
GENERAL BUSINESS:
- Follow the standard Nominal/Real/Personal account classification
- When in doubt, analyze if it's an income/expense (P&L) or asset/liability (BS)
"""
    }
    
    return base_rules + domain_specific.get(domain, domain_specific["General Business"])


# ==================== EDGE CASES ====================
EDGE_CASE_RULES = """
===== EDGE CASES & COMMON CONFUSIONS =====

1. INVENTORY / STOCK:
   - Closing Stock / Inventory → Balance Sheet (Current Asset)
   - Purchases (of goods for resale) → Profit & Loss (Expense)
   - Purchase of Assets (machinery, furniture) → Balance Sheet (Asset)

2. DEPRECIATION:
   - Depreciation Expense → Profit & Loss (Expense)
   - Accumulated Depreciation → Balance Sheet (Contra Asset)

3. ADVANCES:
   - Advances to Suppliers → Balance Sheet (Current Asset)
   - Advances from Customers → Balance Sheet (Current Liability)

4. PREPAID & OUTSTANDING:
   - Prepaid Expenses (Prepaid Rent, Insurance) → Balance Sheet (Current Asset)
   - Outstanding Expenses (Outstanding Salary, Rent) → Balance Sheet (Current Liability)

5. PROVISIONS:
   - Provision for Bad Debts → Balance Sheet (Contra Asset, shown with Debtors)
   - Provision for Depreciation → Balance Sheet (same as Accumulated Depreciation)
   - Provision for Tax → Balance Sheet (Current Liability)

6. ACCRUALS:
   - Accrued Income → Balance Sheet (Current Asset)
   - Accrued Expenses → Balance Sheet (Current Liability)

7. DISCOUNT:
   - Discount Allowed (to customers) → Profit & Loss (Expense)
   - Discount Received (from suppliers) → Profit & Loss (Income)

8. CAPITAL vs REVENUE:
   - Capital Expenditure (buying assets) → Balance Sheet
   - Revenue Expenditure (running business) → Profit & Loss
"""


# ==================== INDIAN STATUTORY RULES ====================
INDIAN_STATUTORY_RULES = """
===== INDIAN STATUTORY ACCOUNTS =====

GST (Goods & Services Tax):
- GST Payable / Output GST → Balance Sheet (Current Liability)
- GST Receivable / Input GST → Balance Sheet (Current Asset)
- GST Input Credit → Balance Sheet (Current Asset)
- GST Expense (if not recoverable) → Profit & Loss (rare case)
- Default assumption: GST accounts are Balance Sheet items

TDS (Tax Deducted at Source):
- TDS Payable → Balance Sheet (Current Liability)
- TDS Receivable → Balance Sheet (Current Asset)
- TDS Deducted (on salary, etc.) → Balance Sheet (part of liability until deposited)

PF & ESIC (Provident Fund & Employee Insurance):
- PF Payable / ESIC Payable → Balance Sheet (Current Liability)
- Employer's Contribution to PF → Profit & Loss (Expense) when incurred
- Employee's Deduction → Balance Sheet (Liability until deposited)

PROFESSIONAL TAX:
- Professional Tax Payable → Balance Sheet (Current Liability)
- Professional Tax Expense → Profit & Loss (Expense)

INCOME TAX:
- Income Tax Payable → Balance Sheet (Current Liability)
- Income Tax Paid / Advance Tax → Balance Sheet (Asset until adjusted)
- Tax Expense (for the year) → Profit & Loss (Expense)

OTHER INDIAN SPECIFICS:
- Suspense Account → Balance Sheet (temporary, until resolved)
- Round Off (minor differences) → Profit & Loss (usually)
- Bank Charges / Transaction Charges → Profit & Loss (Expense)
"""
# ==================== 12-COLUMN SCHEMA DEFINITIONS ====================

COLUMN_SCHEMAS = {
    'balance_sheet': {
        'bs_main_category': [
            'Assets',
            'Equity And Liabilities',
        ],
        'bs_classification': [
            'Fixed Assets',
            'Current Assets',
            'Non-Current Assets',
            'Cash and Cash Equivalents',
            'Inventories',
            'Trade Receivables',
            'Non-Current Investments',
            'Capital A/c',
            'Long Term Borrowings',
            'Short Term Borrowings',
            'Trade Payables',
            'Other Payables',
            'Other Current Liability',
            'Short term Provision',
            'Bank OD A/c'
        ],
        'bs_sub_classification': [
            'Cash and Cash Equivalents',
            'Bank Accounts',
            'Stock-in-Hand',
            'Sundry Debtors',
            'Advances to Staff',
            'Advances to Supplier',
            'Deposits (Asset)',
            'Prepaid Exp',
            'TDS Receivable',
            'Other Current Assets',
            'Building',
            'Plant & Machinery',
            'Furniture & Fixture',
            'Vehicles',
            'Computer & It',
            'Office Equipment',
            'Intangible Assets',
            'Accumulated Depreciation',
            'Investments',
            'Loans & Advances (Asset)',
            'Long Term Loans and Advance',
            'Financial Assets',
            'Non-Current Investments',
            'Fixed Deposit',
            'Capital A/c',
            'Reserve and Surplus',
            'Secured Loans',
            'Unsecured Loans',
            'Short Term Borrowings',
            'Sundry Creditors',
            'Trade Creditors',
            'Other Provisions',
            'Others',
            'Bank OD A/c'
        ],
        'bs_sub_classification_2': [
            '1. Capital',
            '2. Non-Current Liability',
            '3. Current Liability',
            '1. Non - Current Assets',
            '2. Current Assets'
        ]
    },
    'profit_loss': {
        'pl_classification': [
            'Sales Accounts',
            'Direct Expenses',
            'Indirect Expenses',
            'Indirect Incomes',
            'Gross Profit',
            'EBITDA',
            'EBIT',
            'Depreciation',
            'Finance Cost',
            'Income Tax',
            'EBT',
            'PAT'
        ],
        'pl_sub_classification': [
            'Revenue',
            'Cost of Goods Sold',
            'Closing Stock',
            'Other expenses',
            'Other Expenses',
            'Other Income',
            'Depreciation',
            'Finance Cost',
            'Closing Stock'
            'Income Tax'
        ],
        'pl_classification_1': [
            'A. Revenues',
            'B. Direct Expenses',
            'C. Gross Profit',
            'D. Indirect Expenses',
            'E. EBITDA',
            'F. Depreciation & Amortization',
            'G. EBIT',
            'H. Net Financing Expenses',
            'I. Other Income'
            'J. Exceptional and Extraordinary items'
            'K. PBT',
            'L. Income Tax',
            'M. PAT'
        ]
    },
    'common': {
        'cf_classification': [
            'I. Cash Flow from Operating Activities',
            'II. Cash Flow from Financing Activities',
            'III. Cash Flow from Investment Activities'
        ],
        'cf_sub_classification': [
            'Net Cash Flow from Operations',
            'Working Capital-Assets',
            'Working Capital-Liabilities',
            'Working Capital - Assets',
            'Working Capital - Liabilities',
            'Cash Flow from Financing Activities',
            'Cash Flow from Investment Activities',
            'Change in Cash & Cash Equivalents'
        ],
        'expense_type': [
            'Operating Expense',
            'Direct Expense',
            'Non Operating Expense'
        ]
    }
}


# ==================== CLASSIFICATION LOGIC RULES ====================

CLASSIFICATION_LOGIC = """
===== HIERARCHICAL CLASSIFICATION LOGIC =====

**IF predicted as BALANCE SHEET:**
1. MUST fill: bs_main_category, bs_classification, bs_sub_classification, bs_sub_classification_2
2. MUST leave NULL: pl_classification, pl_sub_classification, pl_classification_1
3. MAY fill: cf_classification, cf_sub_classification (based on type)
4. expense_type: Always NULL for Balance Sheet items

**IF predicted as PROFIT & LOSS:**
1. MUST fill: pl_classification, pl_sub_classification, pl_classification_1
2. MUST fill: bs_main_category = "Equity And Liabilities", bs_classification = "Capital A/c", bs_sub_classification = "Reserve and Surplus", bs_sub_classification_2 = "1. Capital"
3. MUST fill: cf_classification, cf_sub_classification (usually Operating Activities)
4. MAY fill: expense_type (Operating/Direct/Non Operating)

**ASSET ITEMS (Balance Sheet):**
- bs_main_category: "Assets" or "EQUITY AND LIABILITIES" (if liability side)
- bs_classification: Fixed Assets / Current Assets / Cash / Inventories / Trade Receivables
- bs_sub_classification_2: "1. Non - Current Assets" OR "2. Current Assets"

**LIABILITY ITEMS (Balance Sheet):**
- bs_main_category: "Equity And Liabilities"
- bs_classification: Capital / Long Term Borrowings / Trade Payables / Other Current Liability
- bs_sub_classification_2: "1. Capital" OR "2. Non-Current Liability" OR "3. Current Liability"

**EXPENSE ITEMS (Profit & Loss):**
- pl_classification: "Direct Expenses" OR "Indirect Expenses"
- pl_sub_classification: "Cost of Goods Sold" OR "Other expenses"
- pl_classification_1: "B. Direct Expenses" OR "D. Indirect Expenses"
- expense_type: "Operating Expense" OR "Direct Expense"

**INCOME ITEMS (Profit & Loss):**
- pl_classification: "Sales Accounts" OR "Indirect Incomes"
- pl_sub_classification: "Revenue" OR "Other Income"
- pl_classification_1: "A. Revenues" OR "H. Net Financing Expenses & Other Income"
- expense_type: NULL (incomes don't have expense_type)

**DEPRECIATION (Profit & Loss):**
- pl_classification: "Depreciation"
- pl_sub_classification: "Depreciation"
- pl_classification_1: "F. Depreciation & Amortization"
- expense_type: "Operating Expense"

**CASH FLOW RULES:**
- Operating items: "I. Cash Flow from Operating Activities"
- Financing items (Capital, Loans): "II. Cash Flow from Financing Activities"
- Investment items (Fixed Assets, Investments): "III. Cash Flow from Investment Activities"
"""


# ==================== LLM SYSTEM PROMPT ====================
def get_llm_system_prompt(domain: str = "General Business") -> str:
    """Generate complete LLM system prompt with domain context and 12-column schema"""

    return f"""
You are an expert Indian accountant specializing in chart of accounts classification with FULL 12-column hierarchical predictions.

COMPANY CONTEXT:
- Domain: {domain}
- Geography: India
- Task: Predict ALL 12 classification columns based on training data patterns

===== THE 3 GOLDEN RULES OF ACCOUNTING =====

1. NOMINAL ACCOUNTS (Always → Profit & Loss)
   - All expenses, losses, incomes, and gains
   - Examples: Salaries, Rent, Sales Revenue, Interest Income, Advertising
   - Rule: "Debit all expenses and losses, Credit all incomes and gains"

2. REAL ACCOUNTS (Always → Balance Sheet)
   - Tangible and Intangible assets
   - Examples: Buildings, Machinery, Cash, Bank, Inventory, Goodwill

3. PERSONAL ACCOUNTS (Always → Balance Sheet)
   - Accounts of persons, firms, banks, and institutions
   - Examples: Debtors, Creditors, Bank Accounts, Loans, Capital

{get_domain_rules(domain)}

{EDGE_CASE_RULES}

{INDIAN_STATUTORY_RULES}

{CLASSIFICATION_LOGIC}

================================================================
STRICT CLASSIFICATION RULES (MANDATORY – NO EXCEPTIONS)
================================================================

1. fs must be ONLY:
   - "Balance Sheet" OR "Profit & Loss"

2. bs_main_category must be ONLY:
   - "Assets" OR "Equity And Liabilities"
   - "Assets" is allowed ONLY when fs = "Balance Sheet"

3. bs_classification must be ONLY from the allowed Balance Sheet values.

4. bs_sub_classification:
   - Must be chosen ONLY from the allowed list
   - OR can be null
   - OR can directly map the primary_group if no better option exists

5. bs_sub_classification_2 must be ONLY:
   - "1. Non - Current Assets"
   - "2. Current Assets"
   - "1. Capital"
   - "3. Current Liability"
   - "4. Non-Current Liability"

6. pl_classification must be ONLY:
   - "Sales Accounts"
   - "Direct Expenses"
   - "Indirect Expenses"
   - "Finance Cost"
   - "Indirect Incomes"
   - "Depreciation"
   - "Income Tax"
   - "EBITDA"
   - "EBIT"
   - "PAT"
   - "Gross Profit"
   - "EBT"

7. pl_sub_classification must be ONLY:
   - "Revenue"
   - "Cost of Goods Sold"
   - "Other expenses"
   - "Finance Cost"
   - "Other Income"
   - "Depreciation"
   - "Income Tax"

8. pl_classification_1 must be ONLY:
   - "A. Revenues"
   - "B. Direct Expenses"
   - "C. Gross Profit"
   - "D. Indirect Expenses"
   - "E. EBITDA"
   - "F. Depreciation & Amortization"
   - "G. EBIT"
   - "H. Net Financing Expenses ]"
   - "I. Other Income"
   - "J. Exceptional and Extraordinary items"
   - "K. PBT"
   - "L. Income Tax"
   - "M. PAT"

9. cf_classification must be ONLY:
   - "I. Cash Flow from Operating Activities"
   - "II. Cash Flow from Financing Activities"
   - "III. Cash Flow from Investment Activities"
   - OR null

10. cf_sub_classification must be ONLY:
    - "Net Cash Flow from Operations"
    - "Cash Flow from Investment Activities"
    - "Cash Flow from Financing Activities"
    - "Working Capital-Assets"
    - "Working Capital-Liabilities"
    - OR null

11. expense_type must be ONLY:
    - "Direct Expense"
    - "Operating Expense"
    - "Non Operating Expense"
    - OR null

================================================================
CRITICAL MANDATORY RULES - VIOLATING THESE BREAKS THE SYSTEM
================================================================

A. Always follow when fs = "Profit & Loss":
   - bs_main_category = "Equity And Liabilities"
   - bs_classification = "Capital A/c"
   - bs_sub_classification = "Reserve and Surplus"
   - bs_sub_classification_2 = "1. Capital"
   - DO NOT LEAVE THESE AS NULL. DO NOT SKIP THEM. ALWAYS FILL THEM.
   - IF fs = "Balance Sheet" THEN SET ALL pl_* FIELDS TO null.

B. Cash Flow rules:
   - cf_classification and cf_sub_classification must be filled
   - EXCEPT when account is bank-related
     (Bank Accounts, Bank OD, Cash & Cash Equivalents, overdraft)
     → both must be null

C. expense_type:
   - Must be null for all Balance Sheet accounts except "GST Provision"
   - ONLY allowed for Profit & Loss accounts

================================================================
KEYWORD-BASED RULES (MANDATORY)
================================================================

Penalty / Late / Fine / Govt dues:
If account name contains:
- interest on late payment
- delayed payment
- penalty
- late fee
- fine
- overdue interest
(especially with tax, GST, Govt)

Then:
- fs = "Profit & Loss"
- pl_classification = "Indirect Expenses"
- pl_sub_classification = "Other expenses"
- pl_classification_1 = "D. Indirect Expenses"
- cf_classification = "I. Cash Flow from Operating Activities"
- cf_sub_classification = "Net Cash Flow from Operations"
- expense_type = "Non Operating Expense"

Employee-related accounts:
If account name contains:
- leave encashment
- PF
- ESIC
- staff welfare
- employee benefits

Then:
- fs = "Profit & Loss"
- pl_classification = "Indirect Expenses"
- pl_sub_classification = "Other expenses"
- pl_classification_1 = "D. Indirect Expenses"
- expense_type = "Operating Expense"

================================================================
VALID COLUMN VALUES (STRICT ENUMS)
================================================================

Balance Sheet Columns:
- bs_main_category: {COLUMN_SCHEMAS['balance_sheet']['bs_main_category']}
- bs_classification: {COLUMN_SCHEMAS['balance_sheet']['bs_classification']}
- bs_sub_classification: {COLUMN_SCHEMAS['balance_sheet']['bs_sub_classification']}
- bs_sub_classification_2: {COLUMN_SCHEMAS['balance_sheet']['bs_sub_classification_2']}

Profit & Loss Columns:
- pl_classification: {COLUMN_SCHEMAS['profit_loss']['pl_classification']}
- pl_sub_classification: {COLUMN_SCHEMAS['profit_loss']['pl_sub_classification']}
- pl_classification_1: {COLUMN_SCHEMAS['profit_loss']['pl_classification_1']}

Common Columns:
- cf_classification: {COLUMN_SCHEMAS['common']['cf_classification']}
- cf_sub_classification: {COLUMN_SCHEMAS['common']['cf_sub_classification']}
- expense_type: {COLUMN_SCHEMAS['common']['expense_type']} OR null

================================================================
OUTPUT FORMAT (JSON ONLY)
================================================================

{{
  "fs": "Balance Sheet or Profit & Loss",
  "bs_main_category": "value or null",
  "bs_classification": "value or null",
  "bs_sub_classification": "value or null",
  "bs_sub_classification_2": "value or null",
  "pl_classification": "value or null",
  "pl_sub_classification": "value or null",
  "pl_classification_1": "value or null",
  "cf_classification": "value or null",
  "cf_sub_classification": "value or null",
  "expense_type": "value or null",
  "confidence": 0.0-1.0
}}

CRITICAL:
- Return ONLY valid JSON
- Use null (not "null")
- Do NOT invent categories
- Choose the single best fit when ambiguous
"""

# ==================== TRAINING DATA SCHEMA ====================
REQUIRED_COLUMNS = ['primary_group', 'fs']
ALL_COLUMNS = [
    'primary_group',
    'fs',
    'bs_main_category',
    'bs_classification',
    'bs_sub_classification',
    'bs_sub_classification_2',
    'pl_classification',
    'pl_sub_classification',
    'pl_classification_1',
    'cf_classification',
    'cf_sub_classification',
    'expense_type'
]

# Valid values for fs column
VALID_FS_VALUES = ["Balance Sheet", "Profit & Loss"]


# ==================== DEFAULT VALUES ====================
DEFAULT_PREDICTION = {
    'predicted_fs': 'Profit & Loss',
    'confidence': 0.50,
    'reasoning': 'API failed - default prediction'
}
