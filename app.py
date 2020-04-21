import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


from urllib.request import urlopen
import json
import numpy as np
import plotly.express as px
import pandas as pd

from covid.callbacks import set_callbacks
from covid.layout import set_layout
from covid import db

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

set_layout(app)
set_callbacks(app)

application = app.server
application.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql://root:superset@127.0.0.1:3306/covid"
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.db.init_app(application)


if __name__ == "__main__":
    app.run_server(debug=True)
