from collections import defaultdict

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
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
    add_tag_to_item,
    get_relationships_for_item,
    add_item_flag,
    get_open_item_flags,
    resolve_item_flag,
    get_management_stats,
    get_main_category_cards,
)

from category_styles import get_category_style
from catalog_config import MAIN_CATEGORIES


app = Flask(__name__)


@app.route("/")
def home():
    stats = get_dashboard_stats()
    categories = get_category_counts()
    mods = get_mod_counts()
    favorites = get_favorites()

    category_cards = get_main_category_cards()

    return render_template(
        "home.html",
        stats=stats,
        categories=categories,
        category_cards=category_cards,
        mods=mods,
        favorites=favorites,
        active_page="dashboard",
    )

@app.route("/catalog")
def catalog():
    items = get_all_items()

    return render_template(
        "catalog.html",
        items=items,
        active_page="catalog",
    )


@app.route("/item/<classname>")
def item_detail(classname):
    item = get_item_by_classname(classname)

    if not item:
        abort(404)

    favorite = is_favorite(classname)
    notes = get_notes_for_item(classname)
    tags = get_tags_for_item(classname)
    relationships = get_relationships_for_item(classname)

    return render_template(
        "item.html",
        item=item,
        favorite=favorite,
        notes=notes,
        tags=tags,
        relationships=relationships,
        active_page="catalog",
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = search_items(query) if query else []

    return render_template(
        "search.html",
        query=query,
        results=results,
        active_page="catalog",
    )


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
        items=items,
        grouped_items=grouped_items,
        active_page="catalog",
    )


@app.route("/category/<category>/<subcategory>")
def subcategory_page(category, subcategory):
    items = [
        item for item in get_items_by_category(category)
        if (item["subcategory"] or "Other") == subcategory
    ]

    category_style = get_category_style(category)

    return render_template(
        "subcategory.html",
        category=category,
        subcategory=subcategory,
        category_style=category_style,
        items=items,
        active_page="catalog",
    )


@app.route("/mods")
def mods():
    mods = get_mod_counts()

    return render_template(
        "mods.html",
        mods=mods,
        active_page="mods",
    )


@app.route("/mod/<mod_name>")
def mod_page(mod_name):
    items = get_items_by_mod(mod_name)

    return render_template(
        "mod.html",
        mod_name=mod_name,
        items=items,
        active_page="mods",
    )


@app.route("/relationships")
def relationships():
    return render_template(
        "relationships.html",
        active_page="relationships",
    )


@app.route("/management")
def management():
    stats = get_management_stats()

    return render_template(
        "management.html",
        stats=stats,
        active_page="management"
    )


@app.route("/management/flags")
def management_flags():
    flags = get_open_item_flags()

    return render_template(
        "management_flags.html",
        flags=flags,
        active_page="management",
    )


@app.route("/management/flags/<int:flag_id>/resolve", methods=["POST"])
def resolve_flag(flag_id):
    resolve_item_flag(flag_id)
    return redirect(url_for("management_flags"))


@app.route("/favorite/<classname>", methods=["POST"])
def favorite_item(classname):
    toggle_favorite(classname)
    return redirect(request.referrer or url_for("catalog"))


@app.route("/pins")
def pins():
    favorites = get_favorites()

    return render_template(
        "pins.html",
        favorites=favorites,
        active_page="dashboard",
    )


@app.route("/pin-open/<classname>")
def pin_open(classname):
    mark_favorite_used(classname)
    return redirect(url_for("item_detail", classname=classname))


@app.route("/notes/<int:note_id>/delete/<classname>", methods=["POST"])
def delete_item_note(note_id, classname):
    delete_note(note_id)
    return redirect(url_for("item_detail", classname=classname))


@app.route("/item/<classname>/tags", methods=["POST"])
def add_item_tag(classname):
    tag = request.form.get("tag", "").strip()

    if tag:
        add_tag_to_item(classname, tag)

    return redirect(url_for("item_detail", classname=classname))


@app.route("/item/<classname>/notes", methods=["POST"])
def add_item_note(classname):
    note = request.form.get("note", "").strip()

    if note:
        add_note_to_item(classname, note)

    return redirect(url_for("item_detail", classname=classname))


@app.route("/item/<classname>/flag", methods=["POST"])
def flag_item(classname):
    issue_type = request.form.get("issue_type")
    note = request.form.get("note")
    suggested_category = request.form.get("suggested_category")
    suggested_subcategory = request.form.get("suggested_subcategory")

    add_item_flag(
        classname=classname,
        issue_type=issue_type,
        note=note,
        created_by="Staff",
        suggested_category=suggested_category,
        suggested_subcategory=suggested_subcategory,
    )

    return redirect(url_for("item_detail", classname=classname))

@app.route("/manage/recategorize", methods=["GET", "POST"])
def recategorize_items():
    search_term = ""
    results = []
    selected_item = None
    message = None

    categories = [
        "Weapons",
        "Clothing",
        "Medical",
        "Food",
        "Tools",
        "Vehicles",
        "Base Building",
        "Electronics",
        "Miscellaneous",
    ]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "search":
            search_term = request.form.get("search_term", "").strip()
            if search_term:
                results = find_items_for_recategory(search_term)

        elif action == "select":
            item_id = request.form.get("item_id")
            selected_item = get_item_by_id(item_id)

        elif action == "save":
            item_id = request.form.get("item_id")
            category = request.form.get("category")
            subcategory = request.form.get("subcategory", "").strip()

            update_item_category(item_id, category, subcategory)

            selected_item = get_item_by_id(item_id)
            message = "Category updated successfully."

    return render_template(
        "manage_recategorize.html",
        search_term=search_term,
        results=results,
        selected_item=selected_item,
        categories=categories,
        message=message,
        active_page="management",
    )


if __name__ == "__main__":
    app.run(debug=True)