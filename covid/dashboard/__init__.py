from flask import Flask
import dash
import dash_bootstrap_components as dbc

from .layout import get_layout
from .callbacks.italy import set_callbacks_italy
from .callbacks.world import set_callbacks_world
from .callbacks.multipage import set_callbacks_page


def configure_dahboard(app: Flask) -> dash.Dash:
    dash_app = dash.Dash(
        "name", server=app, external_stylesheets=[dbc.themes.BOOTSTRAP]
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
    return dash_app
