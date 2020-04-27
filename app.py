import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


from urllib.request import urlopen
import json
import numpy as np
import plotly.express as px
import pandas as pd
import os
import logging

# from covid.callbacks import set_callbacks
from covid.callbacks.multipage import set_callbacks_page
from covid.callbacks.italy import set_callbacks_italy
from covid.layout import get_layout
from covid.db import db


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app.config.suppress_callback_exceptions = True

# Flask configuration
application = app.server
environment_configuration = os.environ.get(
    "CONFIGURATION_SETUP", "covid.config.LocalConfig"
)
application.config.from_object(environment_configuration)
db.init_app(application)


app.layout = get_layout
set_callbacks_page(app)
set_callbacks_italy(app)

if __name__ == "__main__":
    app.run_server(debug=True)
