from flask import Flask, render_template, request

from database import get_all_items, get_item_by_classname, search_items

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


@app.route("/item/<classname>")
def item_detail(classname):
    item = get_item_by_classname(classname)

    return render_template(
        "item.html",
        item=item
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    results = []

    if query:
        results = search_items(query)

    return render_template(
        "search.html",
        query=query,
        results=results
    )

if __name__ == "__main__":
    app.run(debug=True)