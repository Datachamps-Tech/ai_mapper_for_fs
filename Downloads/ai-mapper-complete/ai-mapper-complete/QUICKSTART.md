# 🚀 QUICKSTART - Get Running in 5 Minutes

## ✅ Step-by-Step Guide

### 1️⃣ Install Python (if you don't have it)

**Download:** https://www.python.org/downloads/

**During installation:**
- ✅ Check "Add Python to PATH"
- Click "Install Now"

**Verify installation:**
```bash
python --version
```
Should show: `Python 3.8` or higher

---

### 2️⃣ Open Terminal/Command Prompt

**Windows:**
- Press `Windows + R`
- Type `cmd` and press Enter

**Mac:**
- Press `Command + Space`
- Type `terminal` and press Enter

**Linux:**
- Press `Ctrl + Alt + T`

---

### 3️⃣ Navigate to Project Folder

```bash
# Example for Windows (adjust path to where you extracted the project)
cd C:\Users\YourName\Downloads\ai-mapper

# Example for Mac/Linux
cd ~/Downloads/ai-mapper
```

---

### 4️⃣ Install Dependencies

Copy and paste this command:

```bash
pip install streamlit pandas openpyxl rapidfuzz spacy sentence-transformers openai python-dotenv scikit-learn numpy
```

Then download the AI language model:

```bash
python -m spacy download en_core_web_md
```

⏱️ **This will take 5-10 minutes** (downloads ~100MB)

---

### 5️⃣ Get OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

💰 **Note:** You'll need to add $5-10 credit to your OpenAI account

---

### 6️⃣ Set Your API Key

**Option A: Quick (Temporary)**

**Windows:**
```bash
set OPENAI_API_KEY=sk-your-actual-key-here
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY=sk-your-actual-key-here
```

**Option B: Or enter it in the app sidebar when it runs**

---

### 7️⃣ Initialize Project

```bash
python setup.py
```

This creates sample training data and folder structure.

---

### 8️⃣ Run the App! 🎉

```bash
streamlit run app.py
```

**Your browser will open automatically at:** http://localhost:8501

If it doesn't open, copy the URL from the terminal.

---

## 🎯 First Test

1. Go to **Tab 1: Single Item Test**
2. Type: `Salaries and Wages`
3. Click **🎯 Classify**
4. See the result: **Profit & Loss** ✅

---

## 📊 Try Batch Processing

1. Create Excel file with column: `primary_group`
   ```
   primary_group
   Office Rent
   Cash in Hand
   Sales Revenue
   ```

2. Go to **Tab 2: Batch Processing**
3. Upload your Excel file
4. Click **▶️ Start Processing**
5. Download results! 📥

---

## 🎓 Add Your Own Data

1. Open: `data/training_data.xlsx` in Excel
2. Add your accounting line items:
   - Column A: `primary_group` (e.g., "Travel Expenses")
   - Column B: `fs` (either "Balance Sheet" or "Profit & Loss")
3. Save the file
4. In the app, go to **Tab 3**
5. Click **🔄 Refresh from Excel**

---

## 🆘 Problems?

### "Python not found"
- Reinstall Python with "Add to PATH" checked

### "Module not found"
```bash
pip install -r requirements.txt
```

### "spaCy model not found"
```bash
python -m spacy download en_core_web_md
```

### "OpenAI API error"
- Check your API key is correct
- Make sure you have credits in OpenAI account

### App won't open
- Check if something is using port 8501
- Try: `streamlit run app.py --server.port 8502`

---

## 🎊 You're Done!

**The app is now running on your computer!**

Next steps:
- Customize training data with your accounting items
- Adjust thresholds in Settings
- Process your actual accounting data

---

## 💡 Quick Tips

1. **Save Money:** Add common items to training data to avoid LLM calls
2. **Check Confidence:** Items below 70% need manual review
3. **Use Batch:** Process 100s of items at once
4. **Domain Matters:** Select correct business type in Settings

---

## 📱 Interface Tour

**Sidebar (Left):**
- Company Domain dropdown
- Threshold sliders
- API key input (if needed)
- Session statistics

**Tab 1 - Single Test:**
- Test one item at a time
- See decision trail
- Add to training data
- Save results

**Tab 2 - Batch:**
- Upload Excel file
- Process hundreds of items
- Live progress tracking
- Download results

**Tab 3 - Training Data:**
- View all training data
- Search functionality
- Refresh from Excel
- Download CSV

---

**That's it! Happy classifying! 📊✨**

For detailed documentation, see: README.md
