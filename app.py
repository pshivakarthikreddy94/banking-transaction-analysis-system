from datetime import datetime
from pathlib import Path
import sqlite3

import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "banking.db"
CSV_PATH = BASE_DIR / "data" / "sample_transactions.csv"

app = Flask(__name__)
app.secret_key = "change-this-demo-secret-key"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                account_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL CHECK(amount >= 0),
                merchant TEXT,
                payment_method TEXT,
                status TEXT NOT NULL DEFAULT 'Completed'
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        if count == 0 and CSV_PATH.exists():
            df = pd.read_csv(CSV_PATH)
            df.to_sql("transactions", conn, if_exists="append", index=False)


def load_transactions():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC",
            conn
        )


def add_analysis_columns(df):
    if df.empty:
        return df
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["month"] = df["transaction_date"].dt.strftime("%Y-%m")
    df["month_label"] = df["transaction_date"].dt.strftime("%b %Y")
    df["signed_amount"] = df.apply(
        lambda row: row["amount"] if row["transaction_type"] == "Income" else -row["amount"],
        axis=1
    )
    # Transparent demo rule: flag transactions >= the 95th percentile, with a $1,000 floor.
    threshold = max(1000.0, float(df["amount"].quantile(0.95)))
    df["is_flagged"] = (df["amount"] >= threshold) & (df["status"] == "Completed")
    return df


@app.route("/")
def dashboard():
    df = add_analysis_columns(load_transactions())
    if df.empty:
        metrics = {"total_income": 0, "total_expenses": 0, "net_cashflow": 0,
                   "transaction_count": 0, "flagged_count": 0}
        monthly = []
        category_data = []
        recent = []
        flagged = []
    else:
        income = df.loc[df["transaction_type"] == "Income", "amount"].sum()
        expenses = df.loc[df["transaction_type"] == "Expense", "amount"].sum()
        metrics = {
            "total_income": round(float(income), 2),
            "total_expenses": round(float(expenses), 2),
            "net_cashflow": round(float(income - expenses), 2),
            "transaction_count": int(len(df)),
            "flagged_count": int(df["is_flagged"].sum())
        }
        monthly_df = (df.groupby(["month", "month_label"], as_index=False)
                        .agg(income=("amount", lambda s: s[df.loc[s.index, "transaction_type"] == "Income"].sum()),
                             expenses=("amount", lambda s: s[df.loc[s.index, "transaction_type"] == "Expense"].sum()))
                        .sort_values("month"))
        monthly = monthly_df.to_dict("records")
        expense_df = df[df["transaction_type"] == "Expense"].groupby("category")["amount"].sum()
        category_data = [{"category": k, "amount": round(float(v), 2)}
                         for k, v in expense_df.sort_values(ascending=False).items()]
        recent = df.head(8).fillna("").to_dict("records")
        flagged = df[df["is_flagged"]].head(8).fillna("").to_dict("records")

    return render_template("dashboard.html", metrics=metrics, monthly=monthly,
                           category_data=category_data, recent=recent, flagged=flagged)


@app.route("/transactions")
def transactions():
    df = load_transactions().fillna("")
    search = request.args.get("q", "").strip()
    tx_type = request.args.get("type", "").strip()
    if search:
        mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        df = df[mask]
    if tx_type in {"Income", "Expense"}:
        df = df[df["transaction_type"] == tx_type]
    return render_template("transactions.html", transactions=df.to_dict("records"),
                           q=search, selected_type=tx_type)


@app.route("/transactions/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        try:
            date = datetime.strptime(request.form["transaction_date"], "%Y-%m-%d").date().isoformat()
            amount = float(request.form["amount"])
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")
            values = (
                date, request.form["account_id"].strip(),
                request.form["transaction_type"], request.form["category"],
                request.form["description"].strip(), amount,
                request.form["merchant"].strip(), request.form["payment_method"],
                request.form["status"]
            )
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO transactions
                    (transaction_date, account_id, transaction_type, category, description,
                     amount, merchant, payment_method, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)
            flash("Transaction added successfully.", "success")
            return redirect(url_for("transactions"))
        except (ValueError, KeyError) as exc:
            flash(f"Please check the form: {exc}", "danger")
    return render_template("transaction_form.html")


@app.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    flash("Transaction deleted.", "success")
    return redirect(url_for("transactions"))


@app.route("/insights")
def insights():
    df = add_analysis_columns(load_transactions())
    if df.empty:
        rows = []
        threshold = 1000
    else:
        threshold = max(1000.0, float(df["amount"].quantile(0.95)))
        rows = df[df["is_flagged"]].sort_values("amount", ascending=False).fillna("").to_dict("records")
    return render_template("insights.html", flagged=rows, threshold=round(threshold, 2))


@app.route("/export")
def export_csv():
    df = load_transactions()
    return app.response_class(
        df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )


@app.cli.command("init-db")
def init_db_command():
    initialize_database()
    print(f"Database initialized at {DB_PATH}")


initialize_database()

if __name__ == "__main__":
    app.run(debug=True)
