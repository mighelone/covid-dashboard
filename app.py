#%%
import dash
import dash_core_components as dcc
import dash_html_components as html


from urllib.request import urlopen
import json
import numpy as np
import plotly.express as px
import pandas as pd

from covid.layout import set_layout
from covid.callbacks import set_callbacks


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

set_layout(app)
set_callbacks(app)



if __name__ == "__main__":
    app.run_server(debug=True)