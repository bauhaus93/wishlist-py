import time
from base64 import b64encode
from datetime import datetime

import pytz
from flask import jsonify, make_response, redirect, render_template

from app import app
from app.models import Wishlist


def get_navigation():
    return [("index", "Aktuell"), ("new_products", "Neues"), ("timeline", "Timeline")]


def get_datetime(timestamp, fmt):
    timezone = pytz.timezone("Europe/Berlin")
    return timezone.localize(datetime.fromtimestamp(timestamp)).strftime(fmt)


@app.route("/")
@app.route("/index")
def index():
    last_wishlist = Wishlist.query.order_by(Wishlist.timestamp.desc()).first()
    if last_wishlist:
        products = sorted(last_wishlist.products, key=lambda p: p.price, reverse=True)
        date = get_datetime(last_wishlist.timestamp, "%d.%m.%Y %H:%M")
    else:
        date = get_datetime(time.time(), "%d.%m.%Y %H:%M")
        products = []
    return render_template(
        "index.html", navigation=get_navigation(), date=date, products=products
    )


@app.route("/timeline")
def timeline():
    return render_template("timeline.html", navigation=get_navigation())


@app.route("/new")
def new_products():
    return not_found("")


@app.route("/api/datapoints")
def api_datapoints():
    wishlists = Wishlist.query.order_by(Wishlist.timestamp).all()
    data = {"labels": [], "data": []}
    for wishlist in wishlists:
        data["labels"].append(get_datetime(wishlist.timestamp, "%d.%m.%Y %H:%M"))
        data["data"].append(round(sum(map(lambda p: p.price, wishlist.products)), 2))
    return make_response(jsonify(data), 200)


@app.route("/api/fetchdb")
def api_fetch_db():
    data = None
    with open("app.db", "rb") as f:
        data = f.read()
    if data:
        data_b64 = b64encode(data)
        return make_response(data_b64, 200)
    return internal_error("")


@app.errorhandler(500)
def internal_error(_error):
    return make_response(
        render_template("error500.html", navigation=get_navigation()), 500
    )


@app.errorhandler(404)
def not_found(_error):
    return make_response(
        render_template("error404.html", navigation=get_navigation()), 404
    )
