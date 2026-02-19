# 💻 COMPLETE INSTALLATION GUIDE
## AI Accounting Mapper - From Zero to Running

---

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Install Python](#install-python)
3. [Download the Project](#download-project)
4. [Install Dependencies](#install-dependencies)
5. [Setup OpenAI API](#setup-openai)
6. [Initialize Project](#initialize)
7. [Run the Application](#run-application)
8. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

**Operating System:**
- Windows 10/11
- macOS 10.14 or later
- Linux (Ubuntu 20.04+, Debian, Fedora, etc.)

**Hardware:**
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection (for API calls and installation)

**Software:**
- Python 3.8 or higher
- OpenAI API account (with credits)

---

## 1️⃣ Install Python

### Windows

**Step 1:** Go to https://www.python.org/downloads/

**Step 2:** Click "Download Python 3.12.x" (or latest version)

**Step 3:** Run the installer
- ✅ **IMPORTANT:** Check "Add python.exe to PATH"
- ✅ Check "Install pip"
- Click "Install Now"

**Step 4:** Verify installation
```bash
# Open Command Prompt (Windows + R, type "cmd")
python --version
```
Should show: `Python 3.12.x` or similar

---

### macOS

**Option A: Using Homebrew (Recommended)**
```bash
# Install Homebrew first if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

**Option B: Official Installer**
1. Go to https://www.python.org/downloads/
2. Download macOS installer
3. Run the .pkg file
4. Follow installation wizard

**Verify:**
```bash
python3 --version
```

---

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv

# Verify
python3 --version
pip3 --version
```

---

## 2️⃣ Download the Project

### Option A: Download as ZIP

1. Download the `ai-mapper-complete` folder
2. Extract to a convenient location:
   - **Windows:** `C:\Users\YourName\ai-mapper`
   - **Mac:** `~/Documents/ai-mapper`
   - **Linux:** `~/ai-mapper`

### Option B: Using Git (if installed)

```bash
# Navigate to desired location
cd ~/Documents  # or C:\Users\YourName for Windows

# Clone repository (if available)
git clone <repository-url> ai-mapper
cd ai-mapper
```

---

## 3️⃣ Install Dependencies

### Open Terminal/Command Prompt

**Windows:**
1. Press `Windows + R`
2. Type `cmd`
3. Press Enter

**Mac:**
1. Press `Command + Space`
2. Type `terminal`
3. Press Enter

**Linux:**
1. Press `Ctrl + Alt + T`

---

### Navigate to Project

```bash
# Windows example
cd C:\Users\YourName\ai-mapper

# Mac/Linux example
cd ~/Documents/ai-mapper
```

---

### Install Python Packages

**Run these commands one by one:**

```bash
# Install all requirements
pip install -r requirements.txt
```

**Or install manually if requirements.txt fails:**

```bash
pip install streamlit pandas openpyxl rapidfuzz spacy sentence-transformers openai python-dotenv scikit-learn numpy
```

**For Mac/Linux, use `pip3` instead of `pip`:**
```bash
pip3 install -r requirements.txt
```

⏱️ **This takes 5-10 minutes** (downloads ~500MB)

---

### Download spaCy Language Model

**Windows:**
```bash
python -m spacy download en_core_web_md
```

**Mac/Linux:**
```bash
python3 -m spacy download en_core_web_md
```

⏱️ **This takes 2-3 minutes** (downloads ~40MB)

---

## 4️⃣ Setup OpenAI API

### Get API Key

**Step 1:** Go to https://platform.openai.com/

**Step 2:** Sign in or create account

**Step 3:** Navigate to API Keys
- Click your profile (top right)
- Select "API Keys"
- Or go directly to: https://platform.openai.com/api-keys

**Step 4:** Create new key
- Click "Create new secret key"
- Name it: "AI Accounting Mapper"
- Click "Create"
- **COPY THE KEY** (starts with `sk-`)
- ⚠️ You won't be able to see it again!

**Step 5:** Add credits (if needed)
- Go to "Billing" → "Payment methods"
- Add credit card
- Add $10 credit (recommended)

---

### Set API Key

**Method 1: Environment Variable (Recommended)**

**Windows (Permanent):**
```bash
# Option A: Command line (temporary - lasts until you close terminal)
set OPENAI_API_KEY=sk-your-actual-key-here

# Option B: System Environment Variables (permanent)
# 1. Right-click "This PC" → Properties
# 2. Advanced System Settings
# 3. Environment Variables
# 4. Under "User variables", click New
# 5. Variable name: OPENAI_API_KEY
# 6. Variable value: sk-your-actual-key-here
# 7. Click OK
```

**Mac/Linux (Permanent):**
```bash
# Add to your shell configuration
echo 'export OPENAI_API_KEY="sk-your-actual-key-here"' >> ~/.bashrc

# For macOS with zsh
echo 'export OPENAI_API_KEY="sk-your-actual-key-here"' >> ~/.zshrc

# Reload configuration
source ~/.bashrc  # or source ~/.zshrc for Mac
```

**Method 2: Using .env File**

```bash
# Copy example file
cp .env.example .env

# Edit .env file and add your key
# Use any text editor: notepad .env (Windows) or nano .env (Mac/Linux)
```

**Method 3: Enter in App**
- You can enter the API key in the Streamlit sidebar when the app runs

---

## 5️⃣ Initialize Project

Run the setup script to create sample training data:

**Windows:**
```bash
python setup.py
```

**Mac/Linux:**
```bash
python3 setup.py
```

**Expected output:**
```
🚀 Setting up AI Accounting Mapper...

✅ Created directory: data
✅ Created directory: input  
✅ Created directory: output
✅ Created directory: output/batch_predictions
✅ Created directory: output/single_predictions

✅ Created sample training data: data/training_data.xlsx
   Total rows: 63
   Balance Sheet: 31
   Profit & Loss: 32

✨ Setup complete!

Next steps:
1. Edit data/training_data.xlsx to add your own accounting line items
2. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'
3. Run: streamlit run app.py
```

---

## 6️⃣ Run the Application

**Windows:**
```bash
streamlit run app.py
```

**Mac/Linux:**
```bash
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Your browser should open automatically to: http://localhost:8501**

If it doesn't:
1. Copy the URL from the terminal
2. Paste it in your browser
3. Or manually navigate to: http://localhost:8501

---

## 7️⃣ First Test!

### Single Item Test

1. You should see the AI Accounting Mapper interface
2. Go to **Tab 1: 🔍 Single Item Test**
3. Enter: `Salaries and Wages`
4. Click **🎯 Classify**
5. You should see:
   - Predicted FS: **Profit & Loss**
   - Confidence: **100%**
   - Method: **EXACT** (found in training data)

**Congratulations! It's working! 🎉**

---

### Try Another Example

Try these:
- `Office Rent` → Profit & Loss
- `Cash in Hand` → Balance Sheet
- `GST Payable` → Balance Sheet
- `Insurance Premium` → Profit & Loss

---

## 8️⃣ Troubleshooting

### Common Issues

---

#### ❌ "python: command not found"

**Problem:** Python not installed or not in PATH

**Solution:**
```bash
# Windows: Reinstall Python with "Add to PATH" checked

# Mac: Install via Homebrew
brew install python

# Linux:
sudo apt install python3
```

---

#### ❌ "No module named 'streamlit'"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
# or
pip install streamlit
```

---

#### ❌ "Can't find model 'en_core_web_md'"

**Problem:** spaCy model not downloaded

**Solution:**
```bash
python -m spacy download en_core_web_md
```

---

#### ❌ "OpenAI API error: Unauthorized"

**Problem:** API key not set or incorrect

**Solution:**
1. Check your API key is correct
2. Verify it's set in environment:
   ```bash
   # Windows
   echo %OPENAI_API_KEY%
   
   # Mac/Linux
   echo $OPENAI_API_KEY
   ```
3. Or enter it in the app sidebar

---

#### ❌ "Training data not found"

**Problem:** setup.py not run

**Solution:**
```bash
python setup.py
```

---

#### ❌ "Port 8501 is already in use"

**Problem:** Another Streamlit app is running

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill existing process:
# Windows: Find and close Python processes in Task Manager
# Mac/Linux: killall streamlit
```

---

#### ❌ "Permission denied" errors

**Problem:** Insufficient permissions

**Solution:**
```bash
# Windows: Run Command Prompt as Administrator

# Mac/Linux: Use --user flag
pip install --user -r requirements.txt
```

---

### Still Having Issues?

**Check these:**

1. **Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Pip is working:**
   ```bash
   pip --version
   ```

3. **In correct directory:**
   ```bash
   # You should see app.py and config.py
   ls  # Mac/Linux
   dir  # Windows
   ```

4. **Internet connection:**
   - Required for installation
   - Required for OpenAI API calls

5. **Firewall/Antivirus:**
   - May block pip downloads
   - May block Streamlit server
   - Temporarily disable and retry

---

## 🎊 Success Checklist

✅ Python 3.8+ installed  
✅ All packages installed via pip  
✅ spaCy model downloaded  
✅ OpenAI API key configured  
✅ Project initialized with setup.py  
✅ App running on http://localhost:8501  
✅ First classification successful  

---

## 📚 Next Steps

Now that your app is running:

1. **Customize Training Data**
   - Open `data/training_data.xlsx` in Excel
   - Add your company's accounting line items
   - Refresh in the app (Tab 3)

2. **Adjust Settings**
   - Try different Company Domains
   - Fine-tune thresholds in sidebar

3. **Process Real Data**
   - Create Excel with your line items
   - Use Tab 2 for batch processing

4. **Monitor Usage**
   - Check session stats in sidebar
   - Watch LLM call count (costs money!)

---

## 🎓 Quick Reference

### Start Application
```bash
streamlit run app.py
```

### Stop Application
- Press `Ctrl + C` in the terminal

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Re-initialize
```bash
python setup.py
```

### Check Logs
- Logs appear in the terminal where you ran streamlit
- Check for errors if something doesn't work

---

## 💡 Pro Tips

1. **Keep Terminal Open**
   - Don't close the terminal while using the app
   - Logs and errors appear there

2. **Refresh Browser**
   - If UI seems stuck, refresh the page
   - Or click "Rerun" in top-right

3. **Save Your Work**
   - Training data auto-saves to Excel
   - Batch results save to output/batch_predictions/

4. **Version Control**
   - Use Git to track training data changes
   - Download CSV version from Tab 3

5. **API Costs**
   - Monitor OpenAI usage dashboard
   - Add more training data to reduce LLM calls

---

**You're all set! Enjoy using the AI Accounting Mapper! 📊✨**

For detailed feature documentation, see: [README.md](README.md)  
For quick reference, see: [QUICKSTART.md](QUICKSTART.md)
