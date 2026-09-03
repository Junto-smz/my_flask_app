import sqlite3

from flask import Flask, abort, redirect, render_template, request, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret-key"

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
    return f'{amount:,}円'

def validate_expense_form(category, amount_text, spent_on):
    if spent_on == "":
        return "支出日を入力してください", None
    if category == "":
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
    selected_category = request.args.get("category", "")
    selected_month = request.args.get("month", "")    

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        query = """
                    SELECT id, category, amount, spent_on, memo
                    FROM expenses
                    WHERE 1=1
                """
            
        params = []
            
        if selected_category:
                query += " AND category = ?"
                params.append(selected_category)
            
        if selected_month:
                query += " AND substr(spent_on, 1, 7) = ?"
                params.append(selected_month)
                
        query += " ORDER BY spent_on DESC, id DESC"
        
        expenses = conn.execute(query,params).fetchall()

        category_totals = conn.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM expenses
            GROUP BY category
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
        
        months = conn.execute(
            """
            SELECT DISTINCT substr(spent_on, 1, 7) AS month
            FROM expenses
            WHERE spent_on IS NOT NULL AND spent_on != ''
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
        categories = CATEGORIES,
        selected_category = selected_category,
        months = months,
        selected_month = selected_month
    )


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/trips")
def trips():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        trips = conn.execute(
            """
            SELECT id, title, match_date, opponent, stadium, memo
            FROM trips
            ORDER BY match_date DESC, id DESC
            """
            
        ).fetchall()
    
    return render_template("trips.html",trips=trips)

@app.route("/new_trip", methods=["GET", "POST"])
def new_trip():
    error = None
    title = ""
    match_date = ""
    opponent = ""
    stadium = ""
    memo = ""
    
    if request.method == "POST":
        title = request.form["title"].strip()
        match_date = request.form["match_date"].strip()
        opponent = request.form["opponent"].strip()
        stadium = request.form["stadium"].strip()
        memo = request.form["memo"].strip()

        if title == "":
            error = "遠征名を入力してください。"
        elif match_date == "":
            error = "試合日を入力してください。"
        elif opponent == "":
            error = "対戦相手を入力してください。"
        else:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    """
                    INSERT INTO trips (title, match_date, opponent, stadium, memo)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (title, match_date, opponent, stadium, memo),
                )
            flash("遠征を登録しました。")
            return redirect(url_for("trips"))        
    
    return  render_template(
        "new_trip.html",
        error=error,
        title=title,
        match_date = match_date,
        opponent = opponent,
        stadium = stadium,
        memo = memo
    )

@app.route("/hello/<name>")
def hello_name(name):
    return f"こんにちは、{name}さん！"


@app.route("/expenses/new", methods=["GET", "POST"])
def new_expense():
    error = None
    spent_on = ""
    category = ""
    amount_text = ""
    memo = ""

    if request.method == "POST":
        spent_on = request.form["spent_on"].strip()
        category = request.form["category"].strip()
        amount_text = request.form["amount"].strip()
        memo = request.form["memo"].strip()

        error, amount = validate_expense_form(category, amount_text, spent_on)

        if error is None:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    """INSERT INTO expenses (category, amount, spent_on, memo)
                    VALUES (?, ?, ?, ?)""",
                    (category, amount, spent_on, memo),
                )
            flash("支出を登録できました。")
            return redirect(url_for("index"))

    return render_template(
        "new_expense.html",
        error=error,
        spent_on=spent_on,
        category=category,
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
            """SELECT id, category, amount, spent_on, memo
            FROM expenses
            WHERE id = ?""",
            (expense_id,),
        ).fetchone()

    if expense is None:
        abort(404)

    spent_on = expense["spent_on"] or ""
    category = expense["category"]
    amount_text = str(expense["amount"])
    memo = expense["memo"] or ""

    if request.method == "POST":
        spent_on = request.form["spent_on"].strip()
        category = request.form["category"].strip()
        amount_text = request.form["amount"].strip()
        memo = request.form["memo"].strip()

        error, amount = validate_expense_form(category, amount_text, spent_on)

        if error is None:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    """UPDATE expenses
                    SET category = ?, amount = ?, spent_on = ?, memo = ?
                    WHERE id = ?""",
                    (category, amount, spent_on, memo, expense_id),
                )
            flash("支出を更新しました。")
            return redirect(url_for("index"))

    return render_template(
        "edit_expense.html",
        expense=expense,
        error=error,
        spent_on=spent_on,
        category=category,
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
            SELECT id, category, amount, spent_on, memo
            FROM expenses
            WHERE id = ?
            """,
            (expense_id,)
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
    flash("支出を削除しました。")
    return redirect(url_for("index"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"),404

if __name__ == "__main__":
    app.run(debug=True)
