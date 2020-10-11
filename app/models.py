import time

from app import db


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.Integer, index=True, default=lambda: int(time.time()), nullable=False
    )
    products = db.relationship(
        "Product", secondary="wishlist_product", backref="wishlists", lazy="dynamic"
    )


class WishlistProduct(db.Model):
    whishlist_id = db.Column(db.Integer, db.ForeignKey("wishlist.id"), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), primary_key=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stars = db.Column(db.Float, nullable=False)
    link = db.Column(db.String(128), nullable=True)
    link_image = db.Column(db.String(128), nullable=True)
