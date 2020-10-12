import os

from dotenv import load_dotenv

load_dotenv()
base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(base_dir, "db/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
