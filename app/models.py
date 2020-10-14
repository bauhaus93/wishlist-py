import time

from app import db


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)
    value = db.Column(db.Float, default=None)
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
    quantity = db.Column(db.Integer, default=1, nullable=False)
    item_id = db.Column(db.String(64), nullable=True)
    source_id = db.Column(db.Integer, db.ForeignKey("source.id"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "stars": self.stars,
            "link": self.link,
            "link_image": self.link_image,
            "item_id": self.item_id,
            "source_link": self.source.url if self.source else "",
            "source_name": self.source.name if self.source else "Unbekannt",
        }


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    url = db.Column(db.String(128), nullable=False)
    products = db.relationship("Product", backref="source", lazy="dynamic")

    def __repr__(self):
        return self.name
