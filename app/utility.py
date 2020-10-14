import time
from datetime import datetime

import pytz

from app import query
from app.models import Product, Wishlist


def get_datetime(timestamp, fmt):
    timezone = pytz.timezone("Europe/Berlin")
    return timezone.localize(datetime.fromtimestamp(timestamp)).strftime(fmt)


def format_duration(duration):
    minutes = int(duration) // 60
    hours = minutes // 60
    days = hours // 24
    weeks = days // 7
    if weeks > 0:
        return f"{weeks}w {days % 7}d"
    if days > 0:
        return f"{days}d {hours % 24}h"
    if hours > 0:
        return f"{hours}h"
    if minutes > 0:
        return f"{minutes}m"
    return "Jetzt"


def create_timeline_data(
    start, end=int(time.time()), interval=24 * 3600, datefmt="%d.%m.%Y"
):
    start = (start // 3600) * 3600
    end = (end // 3600) * 3600

    wishlists = (
        Wishlist.query.filter(
            (Wishlist.timestamp >= start) & (Wishlist.timestamp <= end)
        )
        .order_by(Wishlist.timestamp)
        .all()
    )
    if wishlists is None:
        return None
    total_points = 1 + (end - start) // interval
    points = [[] for _i in range(total_points)]
    for wishlist in wishlists:
        interval_begin = (wishlist.timestamp - start) // interval
        points[interval_begin].append(wishlist.value)

    if len(points[0]) == 0:
        pre_wishlists = (
            Wishlist.query.filter(Wishlist.timestamp < start)
            .order_by(Wishlist.timestamp.desc())
            .limit(6)
            .all()
        )
        if pre_wishlists:
            points[0] = list(map(lambda wl: wl.value, pre_wishlists))
        else:
            points[0] = [0.0]

    labels = []
    values = []
    for i in range(total_points):
        if len(points[i]) == 0:
            value = values[i - 1]
        else:
            value = round(sum(points[i]) / len(points[i]), 2)
        labels.append(get_datetime(int(start + i * interval), datefmt))
        values.append(value)
    return labels, values


def create_exended_product_list(products):
    def extend_product(p):
        lifetime = query.get_product_lifetime(p.id)
        return {
            **p.as_dict(),
            "lifetime_formatted": format_duration(lifetime),
            "lifetime": lifetime,
        }

    return list(
        map(
            extend_product,
            sorted(products, key=lambda p: p.price, reverse=True),
        )
    )
