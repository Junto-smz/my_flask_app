import sqlite3

from flask import Flask, abort, redirect, render_template, request, url_for

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


@app.template_filter("yen")
def yen_filter(amount):
    return f"{amount:,}円"


def validate_expense_form(name, amount_text, spent_on):
    if spent_on == "":
        return "支出日を入力してください", None
    if name == "":
        return "カテゴリ名を入力してください", None
    if amount_text == "":
        return "金額を入力してください", None

    try:
        amount = int(amount_text)
    except ValueError:
        return "金額は整数で入力してください", None

    if amount <= 0:
        return "金額は1円以上で入力してください", None

    return None, amount


@app.route("/")
def index():
    app_name = "Jリーグアウェイ遠征家計簿"
    description = "遠征にかかった費用を記録・管理するアプリです。"

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        expenses = conn.execute(
            """SELECT id, name, amount, spent_on, memo
            FROM expenses
            ORDER BY spent_on DESC, id DESC"""
        ).fetchall()

        category_totals = conn.execute(
            """
            SELECT name, SUM(amount) AS total
            FROM expenses
            GROUP BY name
            ORDER BY total DESC
            """
        ).fetchall()

        monthly_totals = conn.execute(
            """
            SELECT substr(spent_on, 1, 7) AS month, SUM(amount) AS total
            FROM expenses
            WHERE spent_on IS NOT NULL AND spent_on != ''
            GROUP BY month
            ORDER BY month DESC
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
        total_amount=total_amount,
        category_totals=category_totals,
        monthly_totals=monthly_totals,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/hello/<name>")
def hello_name(name):
    return f"こんにちは、{name}さん！"


@app.route("/expenses/new", methods=["GET", "POST"])
def new_expense():
    error = None
    spent_on = ""
    name = ""
    amount_text = ""
    memo = ""

    if request.method == "POST":
        spent_on = request.form["spent_on"].strip()
        name = request.form["name"].strip()
        amount_text = request.form["amount"].strip()
        memo = request.form["memo"].strip()

        error, amount = validate_expense_form(name, amount_text, spent_on)

        if error is None:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    """INSERT INTO expenses (name, amount, spent_on, memo)
                    VALUES (?, ?, ?, ?)""",
                    (name, amount, spent_on, memo),
                )
            return redirect(url_for("index"))

    return render_template(
        "new_expense.html",
        error=error,
        spent_on=spent_on,
        name=name,
        amount_text=amount_text,
        memo=memo,
        categories=CATEGORIES,
    )


@app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
def edit_expense(expense_id):
    error = None

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        expense = conn.execute(
            """SELECT id, name, amount, spent_on, memo
            FROM expenses
            WHERE id = ?""",
            (expense_id,),
        ).fetchone()

    if expense is None:
        abort(404)

    spent_on = expense["spent_on"] or ""
    name = expense["name"]
    amount_text = str(expense["amount"])
    memo = expense["memo"] or ""

    if request.method == "POST":
        spent_on = request.form["spent_on"].strip()
        name = request.form["name"].strip()
        amount_text = request.form["amount"].strip()
        memo = request.form["memo"].strip()

        error, amount = validate_expense_form(name, amount_text, spent_on)

        if error is None:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    """UPDATE expenses
                    SET name = ?, amount = ?, spent_on = ?, memo = ?
                    WHERE id = ?""",
                    (name, amount, spent_on, memo, expense_id),
                )
            return redirect(url_for("index"))

    return render_template(
        "edit_expense.html",
        expense=expense,
        error=error,
        spent_on=spent_on,
        name=name,
        amount_text=amount_text,
        memo=memo,
        categories=CATEGORIES,
    )


@app.route("/expenses/<int:expense_id>/delete", methods=["GET"])
def confirm_delete_expense(expense_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        expense = conn.execute(
            """
            SELECT id, name, amount, spent_on, memo
            FROM expenses
            WHERE id = ?
            """,
            (expense_id,),
        ).fetchone()

    if expense is None:
        abort(404)

    return render_template("delete_expense.html", expense=expense)


@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """DELETE FROM expenses
            WHERE id = ?""",
            (expense_id,),
        )
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
