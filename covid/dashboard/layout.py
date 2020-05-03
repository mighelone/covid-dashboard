import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash import Dash

from .components.navbar import get_navbar


def get_layout() -> dbc.Container:
    return dbc.Container(
        [dcc.Location("url"), get_navbar(), dbc.Container(id="container", fluid=True),],
        fluid=True,
    )
