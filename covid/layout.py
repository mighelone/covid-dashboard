from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import datetime as dt

from .components.navbar import get_navbar
from .components.help import get_help_modal
from .components.control_row import get_control_row
from .components.plot_row import get_plot_row


def get_layout() -> dbc.Container:
    return dbc.Container(
        [
            dcc.Location("url"),
            get_navbar(),
            get_help_modal(),
            get_control_row(),
            get_plot_row(),
        ],
        fluid=True,
    )
