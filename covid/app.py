import logging
import os

import dash
import dash_bootstrap_components as dbc
from flask import Flask


from .dashboard.callbacks.italy import set_callbacks_italy
from .dashboard.callbacks.multipage import set_callbacks_page
from .dashboard.callbacks.world import set_callbacks_world
from .dashboard.layout import get_layout
from .db import db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

APP_NAME = "covid-dashboard"


def create_app(testing=False, cli=False) -> Flask:
    app = Flask(APP_NAME)
    environment_configuration = os.environ.get(
        "CONFIGURATION_SETUP", "covid.config.LocalConfig"
    )
    app.config.from_object(environment_configuration)
    dash_app = db.init_app(app)

    @app.route("/api")
    def api():
        return "Covid 19 API"

    return app


def configure_dahboard(app: Flask):
    dash_app = dash.Dash(
        APP_NAME, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    # Since we're adding callbacks to elements that don't exist in the app.layout,
    # Dash will raise an exception to warn us that we might be
    # doing something wrong.
    # In this case, we're adding the elements through a callback, so we can ignore
    # the exception.
    dash_app.config.suppress_callback_exceptions = True

    dash_app.layout = get_layout
    set_callbacks_page(dash_app)
    set_callbacks_italy(dash_app)
    set_callbacks_world(dash_app)


# if __name__ == "__main__":
#     app.run_server(debug=True)
