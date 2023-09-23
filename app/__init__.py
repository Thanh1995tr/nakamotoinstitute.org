import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_caching import Cache
from flask_flatpages import FlatPages
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

db = SQLAlchemy()
pages = FlatPages()
cache = Cache(
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache",
        "CACHE_DEFAULT_TIMEOUT": 1800,
    }
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    pages.init_app(app)

    if app.debug:
        cache.init_app(
            app,
            config={
                "CACHE_TYPE": "null",
                "CACHE_DEFAULT_TIMEOUT": 0,
            },
        )
    else:
        cache.init_app(app)

    if not app.debug:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/sni.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("SNI startup")

    return app
