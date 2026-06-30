import sqlite3
from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)
DATABASE = "database/database.db"

@app.route("/")
def index():
    app_name = "Jリーグアウェイ遠征家計簿"
    description = "遠征にかかった費用を記録・管理するアプリです。"

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        expenses = conn.execute(
            """SELECT id,name,amount
            FROM expenses
            ORDER by id DESC"""
        ).fetchall()
    total_amount = 0
    for expense in expenses:
        total_amount += expense["amount"]
    return render_template(
        "index.html",
        app_name=app_name,
        description=description,
        expenses=expenses,
        total_amount = total_amount
    ) 


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/hello/<name>")
def hello_name(name):
    return f"こんにちは、{name}さん！"

@app.route("/expenses/new",methods = ["GET","POST"])
def new_expense():
   if request.method == "POST":
       name = request.form["name"]
       amount = int(request.form["amount"])
       
       with sqlite3.connect(DATABASE) as conn:
           conn.execute(
               """INSERT INTO expenses (name,amount)
               VALUES (?,?)""",
               (name,amount)
           )
       
       return redirect(url_for("index"))
   return render_template("new_expense.html")

@app.route("/expenses/<int:expense_id>/edit", methods=["GET","POST"])
def edit_expense(expense_id):
    if request.method == "POST":
        name = request.form["name"]
        amount = int(request.form["amount"])
        
        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                """UPDATE expenses
                SET name = ?,amount = ?
                WHERE id = ?""",
                (name,amount,expense_id)
            )
        return redirect(url_for("index"))
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        expense = conn.execute(
            """SELECT id,name,amount
            FROM expenses
            WHERE id = ?""",
            (expense_id,)
        ).fetchone()
    return render_template("edit_expense.html",expense=expense)

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