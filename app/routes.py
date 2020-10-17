import time
from base64 import b64encode
from datetime import datetime

import pytz
from flask import jsonify, make_response, redirect, render_template, url_for

from app import app, cache, db, logger, query
from app.models import Product, Wishlist
from app.scrape_task import update_wishlist_db
from app.utility import (create_exended_product_list, create_timeline_data,
                         get_datetime)

log = logger.get()


def get_navigation():
    return [
        ("index", "Aktuell"),
        ("new_products", "Neues"),
        ("product_archive", "Archiv"),
        ("timeline", "Timeline"),
        ("initiate_fetch", "Fetch"),
    ]


@app.route("/")
@app.route("/index")
@cache.cached(timeout=60)
def index():
    last_wishlist = query.get_last_wishlist()
    if last_wishlist:
        products = create_exended_product_list(last_wishlist.products)
        total_value = last_wishlist.value
        last_change_timestamp = query.get_last_change_timestamp()
        if not last_change_timestamp:
            last_change_timestamp = query.get_first_wishlist().timestamp
        last_change_date = get_datetime(last_change_timestamp, "%d.%m.%Y %H:%M")
    else:
        products = []
        total_value = 0.0
        last_change_date = "Nie"
    date = get_datetime((time.time() // 3600) * 3600, "%d.%m.%Y %H:%M")
    title = f"Forderungen vom {date}"
    return render_template(
        "index.html",
        title=title,
        navigation=get_navigation(),
        date=date,
        last_change_date=last_change_date,
        products=products,
        product_count=len(products),
        total_value=total_value,
    )


@app.route("/timeline")
@cache.cached(timeout=60)
def timeline():
    return render_template(
        "timeline.html", title="Historischer Überblick", navigation=get_navigation()
    )


@app.route("/new")
@cache.cached(timeout=60)
def new_products():
    products = sorted(
        create_exended_product_list(Product.query.all() or []),
        key=lambda p: p["birth_ts"],
        reverse=True,
    )[:5]

    title = "Top 5 Neuheiten"
    return render_template(
        "newest.html",
        title=title,
        navigation=get_navigation(),
        products=products,
    )


@app.route("/archive")
@app.route("/archive/<int:page>")
@cache.cached(timeout=60)
def product_archive(page=1):
    last_wishlist = query.get_last_wishlist()
    product_pagination = Product.query.filter(
        ~Product.id.in_(map(lambda p: p.id, last_wishlist.products))
    ).paginate(page, app.config.get("PAGINATION_PER_PAGE"), True)
    title = "Archiv"
    return render_template(
        "archive.html",
        title=title,
        navigation=get_navigation(),
        products=create_exended_product_list(product_pagination.items),
        pagination=product_pagination,
    )


@app.route("/fetch")
def initiate_fetch():
    update_wishlist_db()
    return redirect(url_for("index"))


@app.route("/api/lastChange")
@cache.cached(timeout=60)
def api_get_last_change_timestamp():
    return jsonify({"lastChange": query.get_last_change_timestamp()})


@app.route("/api/history/day")
@cache.cached(timeout=60)
def api_history_day():
    curr_time = int(time.time())
    (labels, values) = create_timeline_data(
        curr_time - 24 * 3600, curr_time, interval=2 * 3600, datefmt="%H:%M"
    )
    return make_response(jsonify({"labels": labels, "values": values}), 200)


@app.route("/api/history/week")
@cache.cached(timeout=60)
def api_history_week():
    curr_time = int(time.time())
    (labels, values) = create_timeline_data(
        curr_time - 7 * 24 * 3600, curr_time, interval=24 * 3600, datefmt="%d.%m"
    )
    return make_response(jsonify({"labels": labels, "values": values}), 200)


@app.route("/api/history/month")
@cache.cached(timeout=60)
def api_history_month():
    curr_time = int(time.time())
    (labels, values) = create_timeline_data(
        curr_time - 4 * 7 * 24 * 3600,
        curr_time,
        interval=2 * 24 * 3600,
        datefmt="%d.%m",
    )
    return make_response(jsonify({"labels": labels, "values": values}), 200)


@app.route("/api/fetchdb")
def api_fetch_db():
    with open("db/app.db", "rb") as f:
        data = b64encode(f.read())
    return make_response(data, 200)


@app.errorhandler(500)
@cache.cached(timeout=60)
def internal_error(_error):
    return make_response(
        render_template(
            "error500.html", title="Interner Fehler", navigation=get_navigation()
        ),
        500,
    )


@app.errorhandler(404)
@cache.cached(timeout=60)
def not_found(_error):
    return make_response(
        render_template("error404.html", title="404", navigation=get_navigation()),
        404,
    )
