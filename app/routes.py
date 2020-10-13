import time
from base64 import b64encode
from datetime import datetime

import pytz
from flask import jsonify, make_response, redirect, render_template, url_for

from app import app, query
from app.models import Product, Wishlist
from app.scrape_task import update_wishlist_db


def get_navigation():
    return [("index", "Aktuell"), ("new_products", "Neues"), ("timeline", "Timeline")]


def get_datetime(timestamp, fmt):
    timezone = pytz.timezone("Europe/Berlin")
    return timezone.localize(datetime.fromtimestamp(timestamp)).strftime(fmt)


@app.route("/")
@app.route("/index")
def index():
    last_wishlist = query.get_last_wishlist()
    if last_wishlist:
        products = sorted(last_wishlist.products, key=lambda p: p.price, reverse=True)
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
def timeline():
    return render_template(
        "timeline.html", title="Historischer Überblick", navigation=get_navigation()
    )


@app.route("/new")
def new_products():
    products = Product.query.order_by(Product.id.desc()).limit(5)
    title = "Top 5 Neuheiten"
    return render_template(
        "index.html",
        title=title,
        navigation=get_navigation(),
        products=products,
    )


@app.route("/api/datapoints")
def api_datapoints():
    wishlists = Wishlist.query.order_by(Wishlist.timestamp).all()
    data = {"labels": [], "data": []}
    for wishlist in wishlists:
        data["labels"].append(get_datetime(wishlist.timestamp, "%d.%m.%Y %H:%M"))
        data["data"].append(round(sum(map(lambda p: p.price, wishlist.products)), 2))
    return make_response(jsonify(data), 200)


@app.route("/api/forcefetch")
def api_force_fetch():
    update_wishlist_db()
    return redirect(url_for("index"))


@app.route("/api/fetchdb")
def api_fetch_db():
    with open("db/app.db") as f:
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
