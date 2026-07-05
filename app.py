from flask import (
    Flask,
    render_template,
    request,
    redirect,
    abort
)

from database import (
    get_all_items,
    get_item_by_classname,
    search_items,
    get_dashboard_stats,
    get_category_counts,
    get_mod_counts,
    get_items_by_category,
    get_items_by_mod,
    get_favorites,
    is_favorite,
    toggle_favorite,
    mark_favorite_used,
    get_notes_for_item,
    add_note_to_item,
    delete_note,
    get_tags_for_item,
    add_tag_to_item
)
from category_styles import get_category_style

app = Flask(__name__)


@app.route("/")
def home():
    stats = get_dashboard_stats()
    categories = get_category_counts()
    mods = get_mod_counts()
    favorites = get_favorites()

    return render_template(
        "home.html",
        stats=stats,
        categories=categories,
        mods=mods,
        favorites=favorites,
        active_page="dashboard"
    )


@app.route("/catalog")
def catalog():
    items = get_all_items()

    return render_template(
    "catalog.html",
    items=items,
    active_page="catalog"
)

@app.route("/item/<classname>")
def item_detail(classname):
    item = get_item_by_classname(classname)
    favorite = is_favorite(classname)
    notes = get_notes_for_item(classname)
    tags = get_tags_for_item(classname)

    if not item: abort(404)

    favorite = is_favorite(classname)
    notes = get_notes_for_item(classname)

    # ---------- DayZRP Presentation Layer ----------

    # item["spawn_status"] = get_spawn_status(item.get("nominal"))

    # Future
    # item["em_policy"] = get_spawn_policy(item)
    # item["rarity"] = get_rarity(item)
    # item["steam_url"] = ...
    # item["mod_logo"] = ...

    # ----------------------------------------------

    return render_template(
        "item.html",
        item=item,
        favorite=favorite,
        notes=notes,
        tags=tags,
        active_page="catalog"
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
from collections import defaultdict

@app.route("/category/<category>")
def category_page(category):
    items = get_items_by_category(category)

    grouped_items = defaultdict(list)
    for item in items:
        subcategory = item["subcategory"] or "Other"
        grouped_items[subcategory].append(item)

    category_style = get_category_style(category)

    return render_template(
        "category.html",
        category=category,
        category_style=category_style,
        grouped_items=grouped_items,
        active_page="catalog"
    )

@app.route("/mod/<mod_name>")
def mod_page(mod_name):
    items = get_items_by_mod(mod_name)

    return render_template(
        "mod.html",
        mod_name=mod_name,
        items=items,
        active_page="mods"
    )
@app.route("/mods")
def mods():
    mods = get_mod_counts()

    return render_template(
        "mods.html",
        mods=mods,
        active_page="mods"
    )
@app.route("/relationships")
def relationships():
    return render_template(
        "relationships.html",
        active_page="relationships"
    )


@app.route("/management")
def management():
    return render_template(
        "management.html",
        active_page="management"
    )
@app.route("/favorite/<classname>", methods=["POST"])
def favorite_item(classname):
    toggle_favorite(classname)
    return redirect(request.referrer or "/catalog")
@app.route("/pins")
def pins():

    favorites = get_favorites()

    return render_template(
        "pins.html",
        favorites=favorites,
        active_page="dashboard"
    )
@app.route("/pin-open/<classname>")
def pin_open(classname):
    mark_favorite_used(classname)
    return redirect(f"/item/{classname}")

@app.route("/notes/<int:note_id>/delete/<classname>", methods=["POST"])
def delete_item_note(note_id, classname):
    delete_note(note_id)
    return redirect(f"/item/{classname}")

@app.route("/item/<classname>/tags", methods=["POST"])
def add_item_tag(classname):
    tag = request.form.get("tag", "").strip()

    if tag:
        add_tag_to_item(classname, tag)

    return redirect(f"/item/{classname}")

@app.route("/item/<classname>/notes", methods=["POST"])
def add_item_note(classname):
    note = request.form.get("note", "").strip()

    if note:
        add_note_to_item(classname, note)

    return redirect(f"/item/{classname}")

if __name__ == "__main__":
    app.run(debug=True)