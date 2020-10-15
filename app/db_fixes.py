from app import db, logger
from app.models import Wishlist

log = logger.get()


def apply_db_fixes():
    log.info("Applying DB fixes")
    recalculate_content_hashes()


def recalculate_content_hashes():
    log.info("Recalculating wishlist content hashes")
    for wishlist in Wishlist.query.all():
        wishlist.content_hash = wishlist.calculate_content_hash()
    db.session.commit()
