import time

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property

from app import db


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)
    value = db.Column(db.Float, default=None)
    content_hash = db.Column(db.Integer, default=hash(""), nullable=False)
    products = db.relationship(
        "Product", secondary="wishlist_product", backref="wishlists", lazy="dynamic"
    )

    def calculate_content_hash(self):
        return hash("-".join(map(lambda p: str(p.id), self.products)))


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
    item_id = db.Column(db.String(64), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey("source.id"))

    def get_total_lifetime(self):
        on_timestamps = sorted(list(map(lambda wl: wl.timestamp, self.wishlists)))
        all_timestamps = sorted(
            list(
                map(
                    lambda wl: wl.timestamp,
                    Wishlist.query.filter(
                        Wishlist.timestamp >= min(on_timestamps)
                    ).all(),
                )
            )
        )
        lifetime = 0
        for ts in on_timestamps:
            next_index = all_timestamps.index(ts) + 1
            if next_index == len(all_timestamps):
                lifetime += int(time.time()) - ts
            elif next_index > 0:
                lifetime += all_timestamps[next_index] - ts
        return lifetime

    def get_last_wishlist_range(self):
        on_timestamps = sorted(list(map(lambda wl: wl.timestamp, self.wishlists)))
        all_timestamps = sorted(
            list(
                map(
                    lambda wl: wl.timestamp,
                    Wishlist.query.filter(
                        Wishlist.timestamp >= min(on_timestamps)
                    ).all(),
                )
            )
        )
        max_ts = max(on_timestamps)
        max_index = all_timestamps.index(max_ts)
        if max_index + 1 == len(all_timestamps):
            death_ts = None
        else:
            death_ts = all_timestamps[max_index + 1]

        birth_ts = all_timestamps[max_index]
        on_index = on_timestamps.index(max_ts) - 1
        all_index = all_timestamps.index(max_ts) - 1
        while on_index >= 0 and all_index >= 0:
            if on_timestamps[on_index] != all_timestamps[all_index]:
                break
            birth_ts = all_timestamps[all_index]
            on_index -= 1
            all_index -= 1
        return (birth_ts, death_ts)

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


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expires = db.Column(
        db.Integer, default=lambda: int(time.time() + 24 * 3600), nullable=False
    )
    sub_json = db.Column(db.String(256), nullable=False)
    notification_timestamp = db.Column(
        db.Integer, default=lambda: int(time.time()), nullable=False
    )
