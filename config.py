import os

from dotenv import load_dotenv

load_dotenv()
base_dir = os.path.abspath(os.path.dirname(__file__))


def read_file(f):
    with open(f, "r") as f:
        return f.read()


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(base_dir, "db/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PAGINATION_PER_PAGE = 10
    APPLY_DB_FIXES = False

    # USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4230.1 Safari/537.36"
    # USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4215.0 Safari/537.36 Edg/86.0.597.0"
    # USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"
    USER_AGENT = "Chrome/70.0"

    VAPID_PRIVATE = read_file(os.path.join(base_dir, "vapid_private.b64"))
    VAPID_PUBLIC = read_file(
        os.path.join(base_dir, "app", "static", "vapid_public.b64")
    )

    WISHLIST_SOURCES = [
        ("Brivad", "https://www.amazon.de/registry/wishlist/CXTWTCBX97J6"),
        ("Arbeidne", "https://www.amazon.de/hz/wishlist/ls/3KD9WD4CSULN7"),
    ]
