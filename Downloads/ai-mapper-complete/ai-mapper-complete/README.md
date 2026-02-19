# 📊 AI Accounting Mapper

Intelligent Financial Statement Classification System using AI

## 🎯 What This Does

Automatically classifies accounting line items (primary groups) into their correct Financial Statements:
- **Balance Sheet** - Assets, Liabilities, Capital
- **Profit & Loss** - Income, Expenses, Gains, Losses

Uses a smart 5-method cascade:
1. **Exact Match** - Perfect matches (confidence: 100%)
2. **Fuzzy Match** - Similar strings (threshold: 85%)
3. **Semantic Similarity** - Meaning-based using spaCy (threshold: 80%)
4. **Embeddings** - Deep semantic understanding (threshold: 80%)
5. **LLM (GPT-4)** - Intelligent classification with Indian accounting rules

---

## 🚀 Quick Start Guide

### Step 1: Prerequisites

You need:
- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **OpenAI API Key** ([Get API Key](https://platform.openai.com/api-keys))
- **Windows, Mac, or Linux** computer

---

### Step 2: Download the Project

**Option A: Download ZIP**
1. Download this entire folder as ZIP
2. Extract to a location like `C:\Users\YourName\ai-mapper` (Windows) or `~/ai-mapper` (Mac/Linux)

**Option B: Using Git** (if you have it)
```bash
git clone <repository-url>
cd ai-mapper
```

---

### Step 3: Install Python Dependencies

Open Terminal/Command Prompt in the project folder:

**Windows:**
```bash
# Navigate to project folder
cd C:\Users\YourName\ai-mapper

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_md
```

**Mac/Linux:**
```bash
# Navigate to project folder
cd ~/ai-mapper

# Install dependencies
pip3 install -r requirements.txt

# Download spaCy language model
python3 -m spacy download en_core_web_md
```

**⏱️ This will take 5-10 minutes** (downloads ~100MB of AI models)

---

### Step 4: Set Up OpenAI API Key

**Option A: Environment Variable (Recommended)**

**Windows:**
```bash
# Temporary (current session only)
set OPENAI_API_KEY=sk-your-api-key-here

# Permanent (add to System Environment Variables)
# Go to: Control Panel → System → Advanced → Environment Variables
# Create new variable: OPENAI_API_KEY = sk-your-api-key-here
```

**Mac/Linux:**
```bash
# Temporary (current session)
export OPENAI_API_KEY='sk-your-api-key-here'

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Option B: Enter in UI**
- You can also enter the API key directly in the Streamlit sidebar when the app runs

---

### Step 5: Initialize the Project

Run the setup script to create sample training data:

```bash
# Windows
python setup.py

# Mac/Linux
python3 setup.py
```

This creates:
- ✅ `data/training_data.xlsx` - Sample accounting line items (63 examples)
- ✅ Required directories (input, output, etc.)

---

### Step 6: Run the Application

```bash
# Windows
streamlit run app.py

# Mac/Linux  
streamlit run app.py
```

**The app will open automatically in your browser at: http://localhost:8501**

If it doesn't open automatically, copy the URL from the terminal.

---

## 📱 Using the Application

### Tab 1: 🔍 Single Item Test

**Test individual line items:**

1. Enter an accounting line item: e.g., "Social Media Advertising"
2. Click **🎯 Classify**
3. View the result:
   - Predicted Financial Statement
   - Confidence percentage
   - Method used (exact/fuzzy/semantic/embeddings/llm)
   - Decision trail (how each method performed)

**Actions:**
- **➕ Add to Training Data** - Add this classification to your training data
- **💾 Save Test** - Save the result as Excel file
- **🔄 Clear Result** - Clear and test another item

---

### Tab 2: 📁 Batch Processing

**Process multiple items at once:**

1. Prepare Excel file with column: `primary_group`
   ```
   primary_group
   Salaries
   Office Rent  
   Cash in Hand
   ```

2. Upload the Excel file
3. Preview the data (shows first 10 rows)
4. Click **▶️ Start Processing**
5. Watch live progress bar
6. Download results with all classifications

**Output includes:**
- `primary_group` - Original input
- `predicted_fs` - Balance Sheet or Profit & Loss
- `confidence` - 0.0 to 1.0
- `method_used` - Which approach worked
- `matched_training_row` - What it matched against
- `needs_review` - Flag for low confidence (<70%)
- `low_confidence_alternative` - Alternative suggestion

**Resume Feature:**
- If processing stops, the progress is saved
- Next time you can **Resume** from where it stopped!

---

### Tab 3: 💾 Training Data

**Manage your training data:**

- **View Stats**: Total rows, Balance Sheet count, P&L count
- **🔄 Refresh from Excel**: Reload after editing the Excel file
- **📥 Download CSV**: Get CSV version for Git tracking
- **🔍 Search**: Find specific items in training data

**Adding New Data:**
1. Method 1: Use "Add to Training Data" button in Tab 1
2. Method 2: Edit `data/training_data.xlsx` directly in Excel, then click Refresh

---

## ⚙️ Settings (Sidebar)

### Company Domain
Select your business type for better LLM accuracy:
- General Business
- SaaS / IT Services
- Manufacturing
- Retail / E-commerce
- Services / Consulting

### Matching Thresholds
Adjust sensitivity:
- **Fuzzy Match**: 0.70 - 1.0 (default: 0.85)
- **Semantic**: 0.70 - 1.0 (default: 0.80)
- **Embeddings**: 0.70 - 1.0 (default: 0.80)
- **Review Threshold**: 0.50 - 1.0 (default: 0.70)

Lower thresholds = more matches but less confident  
Higher thresholds = fewer matches but more confident

### Session Stats
Monitor your usage:
- Predictions Made
- LLM Calls (costs money!)
- Needs Review count
- Method distribution

---

## 📂 Project Structure

```
ai-mapper/
├── app.py                      # 🎨 Streamlit UI (run this!)
├── config.py                   # ⚙️ All settings & thresholds
├── setup.py                    # 🔧 Initial setup script
├── requirements.txt            # 📦 Python dependencies
│
├── data/
│   ├── training_data.xlsx      # 📊 Your training data (EDIT THIS!)
│   ├── training_data.csv       # 📄 CSV copy for Git
│   ├── training_data.json      # ⚡ Fast-load cache
│   ├── training_embeddings.pkl # 🧠 Pre-computed embeddings
│   └── progress.json           # 💾 Batch processing checkpoint
│
├── input/                      # 📥 Upload batch files here
├── output/
│   ├── batch_predictions/      # 📊 Batch results
│   └── single_predictions/     # 📋 Saved single tests
│
└── src/
    ├── data_loader.py          # 📂 Training data management
    ├── exact_matcher.py        # 1️⃣ Exact matching
    ├── fuzzy_matcher.py        # 2️⃣ Fuzzy matching
    ├── semantic_matcher.py     # 3️⃣ spaCy semantic
    ├── embedding_matcher.py    # 4️⃣ Sentence transformers
    ├── llm_matcher.py          # 5️⃣ GPT-4 classification
    ├── mapper.py               # 🎯 Main orchestrator
    └── utils.py                # 🛠️ Helper functions
```

---

## 🎓 Training Data Format

### Excel Columns

**Required (used now):**
- `primary_group` - The accounting line item name
- `fs` - Either "Balance Sheet" or "Profit & Loss"

**Optional (for future use):**
- `bs_main_category`
- `bs_classification`
- `bs_sub_classification`
- `bs_sub_classification_2`
- `pl_classification`
- `pl_sub_classification`
- `pl_classification_1`
- `cf_classification`
- `cf_sub_classification`
- `expense_type`

### Sample Training Data

| primary_group | fs |
|---------------|-----|
| Cash in Hand | Balance Sheet |
| Salaries and Wages | Profit & Loss |
| Office Rent | Profit & Loss |
| Sundry Debtors | Balance Sheet |

**Start with 50-100 examples, then grow organically!**

---

## 💡 Tips for Best Results

### 1. Build Good Training Data
- Add common line items from your business
- Include variations (e.g., "Rent", "Rent Expense", "Office Rent")
- Use real examples from your accounting system

### 2. Use Consistent Naming
- "Salaries and Wages" vs "Salary Wages" - pick one style
- Be consistent across your training data

### 3. Monitor Confidence
- Items with <70% confidence need review
- If many items need review, add more training data
- Or adjust thresholds in Settings

### 4. Understand Methods
- **Exact** (100%): Perfect match found
- **Fuzzy** (85%+): Very similar text
- **Semantic** (80%+): Similar meaning
- **Embeddings** (80%+): Deep understanding
- **LLM** (varies): AI reasoning (costs money)

### 5. LLM Cost Management
- First 4 methods are FREE
- LLM calls cost ~$0.01-0.03 per item
- Add common items to training data to avoid LLM calls

---

## 🔧 Troubleshooting

### "spaCy model not found"
```bash
python -m spacy download en_core_web_md
```

### "OpenAI API error"
- Check your API key is correct
- Ensure you have credits in your OpenAI account
- Check internet connection

### "Training data not found"
```bash
python setup.py
```

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Streamlit won't start
```bash
# Windows
pip install --upgrade streamlit

# Mac/Linux
pip3 install --upgrade streamlit
```

### Port 8501 already in use
```bash
streamlit run app.py --server.port 8502
```

---

## 🌟 Advanced Features

### Custom Training Data
Replace the sample data with your own:
1. Open `data/training_data.xlsx` in Excel
2. Delete sample rows
3. Add your accounting line items
4. Save and click "Refresh from Excel" in the app

### Adjust Thresholds
Fine-tune matching sensitivity in the sidebar:
- Lower = more matches (less strict)
- Higher = fewer matches (more strict)

### Export for Git
Download CSV version for version control:
- Click "Download CSV" in Tab 3
- Commit to Git to track changes

---

## 📊 How It Works

### The 3 Golden Rules of Accounting

The LLM uses these fundamental principles:

**1. NOMINAL ACCOUNTS → Profit & Loss**
- All expenses, losses, incomes, gains
- Examples: Salaries, Rent, Sales, Interest

**2. REAL ACCOUNTS → Balance Sheet**
- Tangible/Intangible assets
- Examples: Cash, Buildings, Inventory, Goodwill

**3. PERSONAL ACCOUNTS → Balance Sheet**
- Persons, firms, banks
- Examples: Debtors, Creditors, Loans

### Indian Accounting Specifics

Built-in knowledge of:
- TDS Payable → Balance Sheet
- GST (default) → Balance Sheet
- ESIC/PF Payable → Balance Sheet
- Suspense Account → Balance Sheet

---

## 🆘 Support

### Common Questions

**Q: How much does it cost?**
A: The software is free. Only OpenAI API calls cost money (~$0.01-0.03 per LLM classification).

**Q: Can I use it offline?**
A: First 4 methods work offline. LLM (method 5) needs internet.

**Q: How accurate is it?**
A: With good training data: 85-95% accuracy. LLM fallback handles edge cases.

**Q: Can I add more categories?**
A: Currently only Balance Sheet vs Profit & Loss. Future versions will support all 12 columns.

**Q: Where is my data stored?**
A: Everything is local on your computer. Nothing sent to cloud except OpenAI API calls.

---

## 🚀 Quick Command Reference

```bash
# Install
pip install -r requirements.txt
python -m spacy download en_core_web_md

# Setup
python setup.py

# Run
streamlit run app.py

# Set API Key (Windows)
set OPENAI_API_KEY=sk-your-key

# Set API Key (Mac/Linux)
export OPENAI_API_KEY=sk-your-key
```

---

## 📝 Version

**v1.0.0** - Initial Release

### Features
✅ 5-method classification cascade  
✅ Streamlit UI with 3 tabs  
✅ Batch processing with resume  
✅ Training data management  
✅ Indian accounting rules  
✅ Confidence scoring  
✅ Decision trail visibility  
✅ Professional blue theme  

---

## 📄 License

Private use only. Not for distribution.

---

## 🙏 Credits

Built with:
- Python 3.8+
- Streamlit
- spaCy
- Sentence Transformers
- OpenAI GPT-4
- pandas, openpyxl, rapidfuzz

---

**Happy Classifying! 📊✨**
