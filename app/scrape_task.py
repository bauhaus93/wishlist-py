import logging
import os
import time

from app import app, db, logger, query, scheduler
from app.models import Product, Source, Wishlist, WishlistProduct
from app.scrape import scrape_wishlists

log = logger.get()


@scheduler.task("cron", id="scrape_wishlist_job", minute="0", misfire_grace_time=60)
def update_wishlist_db():
    log.info("Start scraping of wishlists...")
    wishlist_sources = app.config.get("WISHLIST_SOURCES", None)
    wishlist = scrape_wishlists(wishlist_sources)
    if wishlist is None:
        log.error("Couldn't scrape wishlists!")
        return
    log.info("Wishlists successfully scraped, found %d products!" % len(wishlist))
    if need_wishlist_update(wishlist):
        log.info("Wishlist changed, add new one")
        add_wishlist_to_db(wishlist)
    else:
        log.info("Wishlist didn't change, only check for product updates")
        update_products(wishlist)


def need_wishlist_update(wishlist):
    last_wishlist = query.get_last_wishlist()
    if last_wishlist is None:
        return True
    last_products = set(
        map(
            lambda p: (p.item_id, int(p.price * 100), p.quantity),
            last_wishlist.products,
        )
    )
    new_products = set(
        map(lambda p: (p["item_id"], int(p["price"] * 100), p["quantity"]), wishlist)
    )
    return last_products != new_products


def add_wishlist_to_db(wishlist_list):
    log.info("Adding wishlist to database...")

    value = round(sum(map(lambda e: e["price"] * e["quantity"], wishlist_list)))
    wishlist = Wishlist(value=value)
    db.session.add(wishlist)
    new_count = 0
    for entry in wishlist_list:
        product = Product.query.filter_by(item_id=entry["item_id"]).first()
        source = Source.query.filter_by(name=entry["source"]).first()
        if source is None:
            source = Source(name=entry["source_name"], url=entry["source"])
            db.session.add(source)
        if product is None:
            product = Product(
                name=entry["name"],
                price=entry["price"],
                quantity=entry["quantity"],
                stars=entry["stars"],
                link=entry["link"],
                link_image=entry["img_url"],
                item_id=entry["item_id"],
                source=source,
            )
            log.info(
                f"Adding product {product.name[:20]}, price = {product.price:.02f}"
            )
            db.session.add(product)
            new_count += 1
        else:
            update_product(product, entry, source)
        wishlist.products.append(product)
    db.session.commit()
    log.info("Added wishlist to database, got %d new products!" % new_count)


def update_products(products_scraped):
    for product_scraped in products_scraped:
        product = Product.query.filter_by(name=product_scraped["name"]).first()
        if product is None:
            log.warn(
                "Wanted to update product, but product isn't present in db: '%s[..]'"
                % (product_scraped["name"][:20])
            )
            continue
        source = Source.query.filter_by(name=product_scraped["source"]).first()
        if source is None:
            source = Source(
                name=product_scraped["source_name"], url=product_scraped["source"]
            )
            db.session.add(source)
        update_product(product, product_scraped, source)
    db.session.commit()


def update_product(product_db, product_scraped, source):
    if int(product_db.price * 100) != int(product_scraped["price"] * 100):
        log.info(
            "Price of '%s[..]' changed: %.02f -> %.02f"
            % (product_db.name[:20], product_db.price, product_scraped["price"])
        )
        product_db.price = product_scraped["price"]
    if int(product_db.stars * 10) != int(product_scraped["stars"] * 10):
        log.info(
            "Stars of '%s[..]' changed: %.01f -> %.01f"
            % (product_db.name[:20], product_db.stars, product_scraped["stars"])
        )
        product_db.stars = product_scraped["stars"]
    if product_db.quantity != product_scraped["quantity"]:
        log.info(
            "Quantity of '%s[..]' changed: %d -> %d"
            % (product_db.name[:20], product_db.quantity, product_scraped["quantity"])
        )
        product_db.quantity = product_scraped["quantity"]

    if product_db.link != product_scraped["link"]:
        log.info(
            "Link of '%s[..]' changed: %s -> %s"
            % (product_db.name[:20], product_db.link, product_scraped["link"])
        )
        product_db.link = product_scraped["link"]
    if product_db.link_image != product_scraped["img_url"]:
        log.info(
            "Img link of '%s[..]' changed: %s -> %s"
            % (product_db.name[:20], product_db.link_image, product_scraped["img_url"])
        )
        product_db.link_image = product_scraped["img_url"]
    if product_db.item_id != product_scraped["item_id"]:
        log.info(
            "Item ID of '%s[..]' changed: %s -> %s"
            % (product_db.name[:20], product_db.item_id, product_scraped["item_id"])
        )
        product_db.item_id = product_scraped["item_id"]

    if product_db.source is None or product_db.source.url != source.url:
        log.info(
            "Source of '%s[..]' changed: %s -> %s"
            % (product_db.name[:20], product_db.source, source)
        )
        product_db.source = source
