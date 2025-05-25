
# 🚀 Quick Start Guide - Telegram Excel Bot

This guide provides a fast setup method for launching the Telegram Excel Bot on Linux/Mac/Windows.

---

## 📥 Step 1: Clone the Repository
```bash
git clone https://github.com/mohsen9090/telegram-excel-bot.git
cd telegram-excel-bot
```

---

## 🐍 Step 2: Create & Activate Virtual Environment

### Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

---

## 📦 Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔧 Step 4: Configure Bot Token

Open `config.py` and update your bot token:
```python
TOKEN = "YOUR_BOT_TOKEN_HERE"
```

---

## ▶️ Step 5: Run the Bot
```bash
python run_bot.py
```

---

## ☑️ Test Installation
```bash
python3 -c "import telegram, pandas, openpyxl; print('✅ All imports successful')"
```

---

**Created with ❤️ by Mohsen Banihashemi**
