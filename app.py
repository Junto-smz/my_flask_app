from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, Flask!"


@app.route("/about")
def about():
    return "このアプリはJリーグアウェイ遠征の支出を管理する家計簿アプリです。"

@app.route("/hello/<name>")
def hello_name(name):
    return f"こんにちは、{name}さん！"

if __name__ == "__main__":
    app.run(debug=True)