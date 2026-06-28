from flask import Flask,render_template

app = Flask(__name__)


@app.route("/")
def index():
    app_name = "Jリーグアウェイ遠征家計簿"
    description = "遠征にかかった費用を記録・管理するアプリです。"

    expenses = [
        "交通費",
        "宿泊費",
        "チケット代",
        "食費"
    ]

    return render_template(
        "index.html",
        app_name=app_name,
        description=description,
        expenses=expenses
    ) 


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/hello/<name>")
def hello_name(name):
    return f"こんにちは、{name}さん！"

if __name__ == "__main__":
    app.run(debug=True)