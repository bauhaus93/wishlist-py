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
        date = get_datetime(last_wishlist.timestamp, "%d.%m.%Y %H:%M")
    else:
        date = get_datetime(time.time(), "%d.%m.%Y %H:%M")
        products = []
    title = f"Forderungen vom {date}"
    return render_template(
        "index.html",
        title=title,
        navigation=get_navigation(),
        date=date,
        products=products,
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
        create_exended_product_list(query.get_last_wishlist().products),
        key=lambda p: p["lifetime"],
    )[:5]
    title = "Top 5 Neuheiten"
    return render_template(
        "newest.html",
        title=title,
        navigation=get_navigation(),
        products=products,
    )


@app.route("/fetch")
def initiate_fetch():
    update_wishlist_db()
    return redirect(url_for("index"))


@app.route("/api/history/day")
@cache.cached(timeout=60)
def api_history_day():
    (labels, values) = create_timeline_data(
        int(time.time() - 24 * 3600), interval=3600, datefmt="%d.%m.%Y %H:%M"
    )
    return make_response(jsonify({"labels": labels, "values": values}), 200)


@app.route("/api/history/week")
@cache.cached(timeout=3600)
def api_history_week():
    (labels, values) = create_timeline_data(
        int(time.time() - 7 * 24 * 3600), interval=24 * 3600, datefmt="%d.%m.%Y"
    )
    return make_response(jsonify({"labels": labels, "values": values}), 200)


@app.route("/api/history/month")
@cache.cached(timeout=3600)
def api_history_month():
    (labels, values) = create_timeline_data(
        int(time.time() - 4 * 7 * 24 * 3600), interval=24 * 3600, datefmt="%d.%m.%Y"
    )
    return make_response(jsonify({"labels": labels, "values": values}), 200)


@app.route("/api/fetchdb")
def api_fetch_db():
    with open("db/app.db", "rb") as f:
        data = b64encode(f.read())
    return make_response(data, 200)


@app.errorhandler(500)
def internal_error(_error):
    return make_response(
        render_template(
            "error500.html", title="Internal error", navigation=get_navigation()
        ),
        500,
    )


@app.errorhandler(404)
def not_found(_error):
    return make_response(
        render_template(
            "error404.html", title="Page not found", navigation=get_navigation()
        ),
        404,
    )
