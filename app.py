from flask import Flask, render_template, request

from database import (
    get_all_items,
    get_item_by_classname,
    search_items,
    get_dashboard_stats,
    get_category_counts,
    get_mod_counts,
    get_items_by_category,
    get_items_by_mod
)

app = Flask(__name__)


@app.route("/")
def home():
    stats = get_dashboard_stats()
    categories = get_category_counts()
    mods = get_mod_counts()

    return render_template(
        "home.html",
        stats=stats,
        categories=categories,
        mods=mods
    )


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
@app.route("/category/<category>")
def category_page(category):
    items = get_items_by_category(category)

    return render_template(
        "category.html",
        category=category,
        items=items
    )
@app.route("/mod/<mod_name>")
def mod_page(mod_name):
    items = get_items_by_mod(mod_name)

    return render_template(
        "mods.html",
        mod_name=mod_name,
        items=items
    )


if __name__ == "__main__":
    app.run(debug=True)