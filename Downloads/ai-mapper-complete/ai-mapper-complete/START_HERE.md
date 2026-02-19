# 🎯 START HERE - AI Accounting Mapper

Welcome! This is your AI-powered accounting classification system.

---

## 📁 What You Have

You've downloaded the complete AI Accounting Mapper project with:

✅ **Full source code** - All 9 Python modules  
✅ **Streamlit UI** - Professional 3-tab interface  
✅ **Sample data** - 63 pre-loaded accounting items  
✅ **Documentation** - 3 comprehensive guides  
✅ **Ready to run** - Just follow the steps below  

---

## 🚀 3-Step Quick Start

### 1. Read the Right Guide

**Choose based on your experience:**

📘 **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**  
→ New to Python? Start here!  
→ Complete step-by-step with screenshots  
→ Troubleshooting for every issue  

📗 **[QUICKSTART.md](QUICKSTART.md)**  
→ Already have Python?  
→ Get running in 5 minutes  
→ Just the essential commands  

📙 **[README.md](README.md)**  
→ Want full documentation?  
→ Feature explanations  
→ Tips and advanced usage  

---

### 2. Install & Setup

**Minimum requirements:**
```bash
# 1. Install Python 3.8+ (if needed)
# 2. Navigate to this folder
cd path/to/ai-mapper

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download AI model
python -m spacy download en_core_web_md

# 5. Set API key (one of these methods):
export OPENAI_API_KEY='sk-your-key-here'  # Mac/Linux
set OPENAI_API_KEY=sk-your-key-here       # Windows
# OR enter it in the app when it runs

# 6. Initialize project
python setup.py
```

---

### 3. Run the App

```bash
streamlit run app.py
```

**Opens automatically at:** http://localhost:8501

---

## 🎮 How to Use

### Tab 1: Single Item Test
- Test one accounting line item
- See how it's classified
- View decision trail
- Add to training data

### Tab 2: Batch Processing  
- Upload Excel file
- Process 100s of items
- Live progress tracking
- Download results

### Tab 3: Training Data
- View/search all data
- Refresh from Excel
- Download CSV for Git

---

## 📂 Project Structure

```
ai-mapper/
├── START_HERE.md              ← You are here!
├── INSTALLATION_GUIDE.md      ← Detailed setup guide
├── QUICKSTART.md              ← Fast setup guide  
├── README.md                  ← Full documentation
│
├── app.py                     ← Main application (RUN THIS!)
├── config.py                  ← Settings & thresholds
├── setup.py                   ← Initialization script
├── requirements.txt           ← Python dependencies
│
├── data/
│   └── training_data.xlsx     ← Your training data (EDIT THIS!)
│
├── src/
│   ├── mapper.py              ← Main orchestrator
│   ├── exact_matcher.py       ← Method 1: Exact match
│   ├── fuzzy_matcher.py       ← Method 2: Fuzzy match
│   ├── semantic_matcher.py    ← Method 3: spaCy
│   ├── embedding_matcher.py   ← Method 4: Transformers
│   ├── llm_matcher.py         ← Method 5: GPT-4
│   ├── data_loader.py         ← Data management
│   └── utils.py               ← Helper functions
│
├── input/                     ← Upload batch files here
└── output/                    ← Results saved here
```

---

## 💰 Cost Information

**Free to use:**
- First 4 matching methods (exact, fuzzy, semantic, embeddings)
- No limit on usage

**Costs money:**
- Method 5: GPT-4 LLM calls
- Approximately $0.01-0.03 per classification
- Only used when first 4 methods fail

**Cost optimization:**
- Add common items to training data
- Adjust thresholds to match more items
- Monitor LLM call count in sidebar

---

## ✅ First Test Checklist

**After installation, verify it works:**

1. ✅ App opens at http://localhost:8501
2. ✅ No errors in terminal
3. ✅ All 3 tabs are visible
4. ✅ Sidebar shows settings
5. ✅ Try classifying "Salaries and Wages"
6. ✅ Should predict "Profit & Loss" with 100% confidence

**If any step fails:** See INSTALLATION_GUIDE.md → Troubleshooting

---

## 🎯 Your Next Steps

**Week 1: Get Familiar**
- ✅ Run the app successfully
- ✅ Test 5-10 single items
- ✅ Try batch processing with sample file
- ✅ Explore all 3 tabs

**Week 2: Customize**
- ✅ Open `data/training_data.xlsx` in Excel
- ✅ Delete sample data (or keep useful items)
- ✅ Add 20-50 items from your business
- ✅ Refresh in the app (Tab 3)

**Week 3: Use in Production**
- ✅ Prepare your actual accounting data
- ✅ Run batch processing
- ✅ Review low-confidence items
- ✅ Add corrections to training data

**Week 4: Optimize**
- ✅ Adjust thresholds based on results
- ✅ Select correct Company Domain
- ✅ Monitor LLM call count
- ✅ Build comprehensive training data

---

## 🆘 Common Questions

**Q: I don't have Python. Where do I start?**  
A: Read INSTALLATION_GUIDE.md from the beginning

**Q: Python installed. What's the fastest way to run this?**  
A: Follow QUICKSTART.md (5 minutes)

**Q: How do I add my own accounting data?**  
A: Edit `data/training_data.xlsx` in Excel, then refresh in Tab 3

**Q: What if I get errors?**  
A: Check INSTALLATION_GUIDE.md → Troubleshooting section

**Q: How much will OpenAI cost?**  
A: Start with $10 credit. Should last for 300-1000 classifications.

**Q: Can I use this offline?**  
A: First 4 methods work offline. Only LLM needs internet.

**Q: Where are my results saved?**  
A: `output/batch_predictions/` for batch, `output/single_predictions/` for single tests

**Q: How accurate is it?**  
A: With good training data: 85-95% accuracy

**Q: Can I classify things other than Balance Sheet/P&L?**  
A: Not yet. Future versions will support all 12 columns.

---

## 📞 Support

**Documentation:**
- Detailed setup: INSTALLATION_GUIDE.md
- Quick reference: QUICKSTART.md  
- Full features: README.md

**Troubleshooting:**
- See INSTALLATION_GUIDE.md → Section 8
- Check terminal for error messages
- Verify all checklist items above

**Community:**
- Check GitHub issues (if repo is public)
- Share your setup problems in discussions

---

## 🎊 Ready to Start?

**Choose your path:**

1. **Never used Python before?**  
   → Start with: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

2. **Have Python installed?**  
   → Jump to: [QUICKSTART.md](QUICKSTART.md)

3. **Want to understand everything?**  
   → Read: [README.md](README.md)

---

## 🌟 Quick Commands Reference

```bash
# Navigate to project
cd path/to/ai-mapper

# Install everything
pip install -r requirements.txt
python -m spacy download en_core_web_md

# Set API key (choose one)
export OPENAI_API_KEY='sk-your-key'  # Mac/Linux
set OPENAI_API_KEY=sk-your-key       # Windows

# Initialize
python setup.py

# Run
streamlit run app.py

# Stop
Ctrl + C (in terminal)
```

---

**You've got everything you need! Let's get started! 🚀**

**Next:** Open [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) or [QUICKSTART.md](QUICKSTART.md)
