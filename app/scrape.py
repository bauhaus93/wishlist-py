#!/bin/env python

import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app import logger

log = logger.get()


def scrape_wishlist(url, wishlist_name, tries=5, timeout=5.0):
    log.info("Scraping wishlist '%s' from '%s'" % (wishlist_name, url))
    domain = urlparse(url).netloc
    headers = {
        "User-Agent": "Chrome/51.0",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    for i in range(tries):
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            break
        if i + 1 < tries:
            log.warn(
                f"Got http {result.status_code}, try {i + 1}/{tries}, retrying in {timeout} secs..."
            )
            time.sleep(2.0)

    if result.status_code != 200:
        log.error("Could not retrieve wishlist after {tries} tries!")
        return None

    soup = BeautifulSoup(result.text, "html.parser")

    list_items = soup.find(id="g-items")

    products = []

    for item in list_items.find_all("li"):
        price = None
        name = None
        stars = None
        link = None
        img_url = None
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
        }
        if any(map(lambda v: v is None, product.values())):
            log.error("Could not find all values for product: %s" % product)
            return None

        products.append(product)
    return products


def scrape_wishlists(name_url_pairs):
    if name_url_pairs is None:
        return None
    wishlists = []
    for (name, url) in name_url_pairs:
        wishlist = scrape_wishlist(url, name)
        if wishlist is None:
            return None
        wishlists.extend(wishlist)
    return wishlists


# if __name__ == "__main__":
# urls = [
#     "https://www.amazon.de/registry/wishlist/CXTWTCBX97J6",
#     "https://www.amazon.de/hz/wishlist/ls/3KD9WD4CSULN7",
# ]

# wishlists = []
# for url in urls:
#     wishlist = scrape_wishlist(url)
#     if wishlist:
#         wishlists.extend(wishlist)
# total_price = reduce(lambda acc, e: acc + e["price"], wishlists, 0.0)
# print(f"items: {len(wishlists)} | total price: € {total_price:6.2f}")
