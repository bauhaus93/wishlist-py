#!/bin/env python

import logging

from config import Config
from flask import Flask, url_for
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

FORMAT = r"[%(asctime)-15s] %(levelname)s - %(message)s"
DATE_FORMAT = r"%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)


from app import models, routes, scrape_task
