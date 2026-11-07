# Banking Transaction Analysis System

A beginner-friendly Python + Flask web application for exploring synthetic banking transactions. It includes a dashboard, transaction search/filtering, manual transaction entry, CSV export, and a simple explainable high-value transaction review rule.

> **Important:** This is an educational demo. It does not connect to a real bank, process payments, provide financial advice, or detect fraud reliably. Use only synthetic or properly anonymized data. Never commit bank statements, account credentials, API keys, or personal information.

## Features

- Dashboard with income, expenses, net cash flow, transaction count, and review count
- Monthly income/expense summary
- Expense totals by category
- Transaction list with keyword search and type filter
- Add and delete demo transactions
- Export transactions to CSV
- Rule-based review queue for large transactions

## Technology

- Python 3.10+
- Flask
- SQLite
- Pandas
- HTML, CSS, JavaScript, Chart.js (loaded from CDN)

## Folder structure

```text
banking_transaction_analysis_system/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── sample_transactions.csv
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── charts.js
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── transactions.html
    ├── transaction_form.html
    └── insights.html
```

The SQLite database is created automatically at `data/banking.db` when the app starts. It is excluded from Git by `.gitignore`.

## Run on Windows (VS Code)

1. Install Python 3.10 or newer.
2. Open this project folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv venv
   ```

5. Activate it:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this once in that terminal and retry:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```

6. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Start the app:

   ```powershell
   python app.py
   ```

8. Open <http://127.0.0.1:5000> in your browser.

## Demo review rule

The Insights page flags completed transactions whose amount is at least the larger of:
- ₹1,000 (demo threshold), or
- the 95th percentile of amounts in the current dataset.

This is only a transparent demonstration rule. It is not a trained fraud model and can produce false positives and false negatives.

## Reset demo data

Stop the app, delete `data/banking.db`, then run `python app.py` again. The database will be recreated from `data/sample_transactions.csv`.

## Push to GitHub

Create an empty public repository on GitHub, then in the VS Code terminal run:

```powershell
git init
git add .
git commit -m "Initial banking transaction analysis system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the URL with your repository URL. If `origin` already exists, use:

```powershell
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

For future changes:

```powershell
git add .
git commit -m "Describe your update"
git push
```

Before pushing, check `git status` and confirm that no real customer data, bank statements, credentials, or local database are staged.
