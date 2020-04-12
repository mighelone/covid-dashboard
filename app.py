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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

set_layout(app)
set_callbacks(app)

application = app.server


if __name__ == "__main__":
    app.run_server(debug=True)
