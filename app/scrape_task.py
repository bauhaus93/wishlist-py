import logging
import os
import time

from app import db, logger, query, scheduler
from app.models import Product, Wishlist, WishlistProduct
from app.scrape import scrape_wishlists

log = logger.get()


# @scheduler.task("cron", id="scrape_wishlist_job", minute="0", misfire_grace_time=60)
@scheduler.task("interval", id="scrape_wishlist_job", seconds=10)
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
    if need_wishlist_update(wishlist):
        log.info("Wishlist needs update")
        add_wishlist_to_db(wishlist)
    else:
        log.info("No wishlist update needed")


def need_wishlist_update(wishlist):
    last_wishlist = query.get_last_wishlist()
    diff = int(time.time()) - last_wishlist.timestamp
    log.info(
        "Last wishlist timestamp is %02dh%02dm old"
        % (int(diff / 3600), int(diff % 3600) / 60)
    )
    if time.time() - last_wishlist.timestamp >= 24 * 3600:
        return True
    last_products = set(map(lambda p: p.name, last_wishlist.products))
    new_products = set(map(lambda p: p["name"], wishlist))
    return last_products.union(new_products) != new_products


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
        else:
            if int(product.price * 100) != int(entry["price"] * 100):
                log.info(
                    "Price of '%s[..]' changed: %.02f -> %.02f"
                    % (product.name[:20], product.price, entry["price"])
                )
                product.price = entry["price"]
            if int(product.stars * 10) != int(entry["stars"] * 10):
                log.info(
                    "Stars of '%s[..]' changed: %.01f -> %.01f"
                    % (product.name[:20], product.stars, entry["stars"])
                )
                product.stars = entry["stars"]
            if product.link != entry["link"]:
                log.info(
                    "Link of '%s[..]' changed: %s -> %s"
                    % (product.name[:20], product.link, entry["link"])
                )
                product.link = entry["link"]
            if product.link_image != entry["img_url"]:
                log.info(
                    "Img link of '%s[..]' changed: %s -> %s"
                    % (product.name[:20], product.link_image, entry["img_url"])
                )
                product.link_image = entry["img_url"]

        wishlist.products.append(product)
    db.session.commit()
    log.info("Added wishlist to database, got %d new products!" % new_count)
