import logging
import os

from app import db, scheduler
from app.models import Product, Wishlist, WishlistProduct
from app.scrape import scrape_wishlists

log = logging.getLogger(__name__)


@scheduler.task(
    "cron", id="scrape_wishlist_job", hour="0,6,12,18", misfire_grace_time=60
)
# @scheduler.task("interval", id="scrape_wishlist_job", seconds=10)
def update_wishlist_db():
    log.info("Start scraping of wishlists...")
    env_wl = os.environ.get("WISHLISTS", None)
    if env_wl is None:
        log.error("Environment variable 'WISHLISTS' missing, can't update wishlist!")
        return
    wishlist_urls = env_wl.split(" ")
    wishlist = scrape_wishlists(wishlist_urls)
    if wishlist is None:
        log.error("Couldn't scrape wishlists!")
        return
    log.info("Wishlists successfully scraped, found %d products!" % len(wishlist))
    add_wishlist_to_db(wishlist)


def add_wishlist_to_db(wishlist_list):
    log.info("Adding wishlist to database...")
    wishlist = Wishlist()
    db.session.add(wishlist)
    new_count = 0
    for entry in wishlist_list:
        product = Product.query.filter_by(name=entry["name"]).first()
        if product is None:
            product = Product(
                name=entry["name"],
                price=entry["price"],
                stars=entry["stars"],
                link=entry["link"],
                link_image=entry["img_url"],
            )
            db.session.add(product)
            new_count += 1
        wishlist.products.append(product)
    db.session.commit()
    log.info("Added wishlist to database, got %d new products!" % new_count)
