import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


DATABASE = "database/database.db"

CATEGORIES = [
    "交通費",
    "宿泊費",
    "チケット代",
    "食費",
    "グッズ代",
    "その他",
]

def validate_expense_form(name, amount_text, spent_on):
    if spent_on == "":
        return "支出日を入力してください",None
    if name == "":
        return "カテゴリ名を入力してください",None
    
    if amount_text =="":
        return "金額を入力してください",None
    
    amount = int(amount_text)
    
    if amount <= 0:
        return "金額は1円以上で入力してください",None
    
    return None,amount


@app.route("/")
def index():
    app_name = "Jリーグアウェイ遠征家計簿"
    description = "遠征にかかった費用を記録・管理するアプリです。"

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        expenses = conn.execute(
            """SELECT id,name,amount,spent_on
            FROM expenses
            ORDER by id DESC"""
        ).fetchall()
        
        category_totals = conn.execute(
            """
            SELECT name, SUM(amount) AS total
            FROM expenses
            GROUP BY name
            ORDER BY total DESC
            """
        ).fetchall()
        
    total_amount = 0
    for expense in expenses:
        total_amount += expense["amount"]
    return render_template(
        "index.html",
        app_name=app_name,
        description=description,
        expenses=expenses,
        total_amount = total_amount,
        category_totals = category_totals
    ) 


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/hello/<name>")
def hello_name(name):
    return f"こんにちは、{name}さん！"


@app.route("/expenses/new",methods = ["GET","POST"])
def new_expense():
    error = None
    spent_on = ""
    name = ""
    amount_text = ""
    if request.method == "POST":
        spent_on = request.form["spent_on"].strip()
        name = request.form["name"].strip()
        amount_text = request.form["amount"].strip()
        
        error,amount = validate_expense_form(name,amount_text,spent_on)
        
        if error is None:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    """INSERT INTO expenses (name,amount,spent_on)
                    VALUES (?,?,?)""",
                    (name,amount,spent_on)
                )
            return redirect(url_for("index"))
        
    return render_template(
                        "new_expense.html",
                        error = error,
                        spent_on = spent_on,
                        name = name,
                        amount_text = amount_text,
                        categories = CATEGORIES)
                        


@app.route("/expenses/<int:expense_id>/edit", methods=["GET","POST"])
def edit_expense(expense_id):
    error = None
    
    with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            expense = conn.execute(
                """SELECT id,name,amount,spent_on
                FROM expenses
                WHERE id = ?""",
                (expense_id,)
            ).fetchone()
    
    spent_on = expense["spent_on"] or ""        
    name = expense["name"]
    amount_text  = str(expense["amount"])
    
    if request.method == "POST":
        spent_on = request.form["spent_on"].strip()
        name = request.form["name"].strip()
        amount_text = request.form["amount"].strip()
        
        error,amount = validate_expense_form(name,amount_text,spent_on)
        
        if error is None:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    """UPDATE expenses
                    SET name = ?, amount = ?, spent_on = ?
                    WHERE id = ?""",
                    (name,amount,spent_on,expense_id)
                )
                return redirect(url_for("index"))
            
    return render_template(
                        "edit_expense.html",
                        expense=expense,
                        error = error,
                        spent_on = spent_on,
                        name = name,
                        amount_text = amount_text,
                        categories = CATEGORIES)

@app.route("/expenses/<int:expense_id>/delete",methods=["POST"])
def delete_expense(expense_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """DELETE FROM expenses 
            WHERE id = ?""",
            (expense_id,)
        )
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
