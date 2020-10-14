#!/bin/env python

import os
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from app import logger

log = logger.get()


def scrape_wishlist(url, wishlist_name, driver, scroll_count=5, scroll_sleeptime=2.0):
    log.info("Scraping wishlist '%s' from '%s'" % (wishlist_name, url))
    domain = urlparse(url).netloc

    driver.get(url)
    screen_height = driver.execute_script("return window.screen.height;")
    for i in range(scroll_count):
        time.sleep(scroll_sleeptime)
        driver.execute_script(
            "window.scrollTo(0, {screen_height}*{i});".format(
                screen_height=screen_height, i=i
            )
        )

    soup = BeautifulSoup(driver.page_source, "html.parser")

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
            return None

        products.append(product)
    return products


def scrape_wishlists(name_url_pairs):
    if name_url_pairs is None:
        return None
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    wishlists = []
    for (name, url) in name_url_pairs:
        wishlist = scrape_wishlist(url, name, driver)
        if wishlist is None:
            wishlists = None
            break
        wishlists.extend(wishlist)

    driver.close()
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
