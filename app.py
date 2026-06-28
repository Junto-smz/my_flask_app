from flask import Flask,render_template

app = Flask(__name__)


@app.route("/")
def index():
    app_name = "Jリーグアウェイ遠征家計簿"
    description = "遠征にかかった費用を記録・管理するアプリです。"

    expenses = [
        {"name": "交通費", "amount": 12000},
        {"name": "宿泊費", "amount": 8000},
        {"name": "チケット代", "amount": 3500},
        {"name": "食費", "amount": 2500}
    ]
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

if __name__ == "__main__":
    app.run(debug=True)