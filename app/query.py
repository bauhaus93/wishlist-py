from app.models import Wishlist


def get_last_wishlist():
    return Wishlist.query.order_by(Wishlist.timestamp.desc()).first()
