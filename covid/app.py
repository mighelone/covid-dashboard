import logging
import os

import dash
from flask import Flask, jsonify

from .dashboard import configure_dahboard

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
    dash_app = configure_dahboard(app)

    @app.route("/api")
    def api():
        from .db import ItalyRegion
        from .api.resources.italy.region import ItalyRegionSchema

        schema = ItalyRegionSchema(many=True)
        query = ItalyRegion.query
        res = schema.dump(query)
        return jsonify(res)

    @app.route("/")
    def dash_app():
        return dash_app.index()

    return app
