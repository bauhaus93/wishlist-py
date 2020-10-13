from app.models import Product, Wishlist


def get_last_wishlist():
    return Wishlist.query.order_by(Wishlist.timestamp.desc()).first()


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
    return last_wishlist.timestamp - first_wishlist.timestamp
