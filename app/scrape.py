#!/bin/env python

import os
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app import logger

log = logger.get()


def scrape_wishlist(url, wishlist_name, tries=5, try_timeout=3.0):
    log.info("Scraping for wishlist '%s'" % wishlist_name)
    domain = urlparse(url).netloc

    for i in range(tries):
        response = requests.get(url, headers={"User-Agent": "Chrome/70.0"})
        if response.status_code == 200:
            break
        else:
            log.warn("Received http {response.status_code}, try {i+1}/{tries}")
            time.sleep(try_timeout)
    if response.status_code != 200:
        log.error("Couldn't retrieve url after {tries}!")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    list_items = soup.find(id="g-items")

    products = []

    for item in list_items.find_all("li"):
        price = None
        name = None
        stars = 0.0
        link = None
        img_url = None
        quantity = None
        item_id = item.get("data-itemid", None)
        try:
            price_str = item.get("data-price", None)
            if price_str:
                price = float(price_str)
        except ValueError:
            log.error("Could not convert price to float, string was '%s'" % price_str)

        img_tag = item.find("img")
        if img_tag:
            img_url = img_tag.get("src", None)
        else:
            log.error("Could not find img tag for product entry")

        for span in item.findAll("span"):
            if "itemRequested_" in span.get("id", ""):
                try:
                    quantity = int(span.string)
                except ValueError:
                    log.error(
                        "Could not convert item quantity to int, string was '%s'" % span
                    )

        for links in item.findAll("a"):
            if "itemName" in links.get("id", ""):
                name = links.string
                link = domain + links.get("href", "")
            elif "reviewStarsPopoverLink" in links.get("class", ""):
                star_string = links.get("aria-label", None)
                if star_string:
                    star_string_split = star_string.split(" ")[0]
                    try:
                        stars = float(star_string_split)
                    except ValueError:
                        log.error(
                            "Could not convert stars to float, full field was '%s' % star_string"
                        )
                        stars = None
        if link:
            link = "https://" + link

        product = {
            "price": price,
            "name": name,
            "link": link,
            "stars": stars,
            "img_url": img_url,
            "source": url,
            "source_name": wishlist_name,
            "item_id": item_id,
            "quantity": quantity,
        }
        if any(map(lambda v: v is None, product.values())):
            log.error("Could not find all values for product: %s" % product)
            return []

        products.append(product)
    for link in list_items.findAll("a"):
        link_class = link.get("class", None)
        if (
            link_class
            and "g-visible-no-js" in link_class
            and "wl-see-more" in link_class
        ):
            next_link = link.get("href", None)
            if next_link:
                next_link = "https://" + domain + next_link
                log.info(f"Found link to more items, following it")
                products.extend(
                    scrape_wishlist(next_link, wishlist_name, tries, try_timeout)
                )
                break

    return products


def scrape_wishlists(name_url_pairs):
    if name_url_pairs is None:
        log.error("Received no name/urls pairs for scraping!")
        return []
    wishlists = []
    for (name, url) in name_url_pairs:
        wishlist = scrape_wishlist(url, name)
        wishlists.extend(wishlist)
    return wishlists


if __name__ == "__main__":
    urls = [
        ("a", "https://www.amazon.de/registry/wishlist/CXTWTCBX97J6"),
        ("b", "https://www.amazon.de/hz/wishlist/ls/3KD9WD4CSULN7"),
    ]

    wishlist = scrape_wishlists(urls)
    for item in wishlist:
        print(item)
    total_price = sum(map(lambda e: e["price"], wishlist))
    print(f"items: {len(wishlist)} | total price: € {total_price:6.2f}")
