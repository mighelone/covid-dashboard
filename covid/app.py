import logging
import os

import dash
from flask import Flask, jsonify
from flask_smorest import Api

from .dashboard import configure_dahboard
from .api import register_api

# from .db import db
from .extension import db, ma

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

APP_NAME = "covid-dashboard"


def create_app(testing=False, cli=False) -> Flask:
    app = Flask(APP_NAME, instance_relative_config=False)
    environment_configuration = os.environ.get(
        "CONFIGURATION_SETUP", "covid.config.LocalConfig"
    )
    app.config.from_object(environment_configuration)
    db.init_app(app)
    ma.init_app(app)

    register_api(app)

    dash_app = configure_dahboard(app)

    @app.route("/")
    def dash_app():
        return dash_app.index()

    return app
