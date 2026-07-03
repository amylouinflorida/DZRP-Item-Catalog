from flask import Flask, render_template
from database import get_all_items

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/catalog")
def catalog():

    items = get_all_items()

    return render_template(
        "catalog.html",
        items=items
    )


if __name__ == "__main__":
    app.run(debug=True)