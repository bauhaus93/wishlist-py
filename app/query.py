import time

from app.models import Product, Wishlist


def get_last_wishlist():
    return Wishlist.query.order_by(Wishlist.timestamp.desc()).first()


def get_first_wishlist():
    return Wishlist.query.order_by(Wishlist.timestamp.asc()).first()


def get_last_change_timestamp():
    last_wishlist = get_last_wishlist()
    first_diff_wishlist = (
        Wishlist.query.filter(Wishlist.content_hash != last_wishlist.content_hash)
        .order_by(Wishlist.timestamp.desc())
        .first()
    )
    if first_diff_wishlist:
        return first_diff_wishlist.timestamp
    return None


def get_product_lifetime(product_id):
    wishlists = sorted(
        Product.query.get(product_id).wishlists, key=lambda w: w.timestamp
    )
    if len(wishlists) == 0:
        return 0
    first_wishlist = wishlists[0]
    last_wishlist = first_wishlist
    for wishlist in wishlists[1:]:
        if wishlist.id != last_wishlist.id + 1:
            return last_wishlist.timestamp - first_wishlist.timestamp
        last_wishlist = wishlist
    return int(time.time()) - first_wishlist.timestamp
