from dash import Dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import datetime as dt
from typing import List, Optional
import os
import dash
from flask import current_app
from sqlalchemy import func

import logging

from . import data  # import get_italy_map_region, get_db_region_data
from . import db
from .plots.maps import generate_map_region
from .plots.bar import generate_bar_plot_overall, generate_bar_plot_selected

log = logging.getLogger(__name__)

log.info("Loading data...")
map_data_region = data.get_italy_map_region()


def update_xaxis(fig: go.Figure, relayout) -> go.Figure:
    """Update fig xaxis with relayout
    
    Arguments:
        fig {go.Figure} -- Plotly fig
        relayout {[type]} -- [description]
    
    Returns:
        go.Figure -- modified figure
    """
    if relayout:
        if "xaxis.range[0]" in relayout:
            fig = fig.update_layout(
                xaxis=go.layout.XAxis(
                    range=[relayout["xaxis.range[0]"], relayout["xaxis.range[1]"],]
                )
            )
    return fig


def set_callbacks(app: Dash):
    @app.callback(
        Output(component_id="map-plot-italy", component_property="figure"),
        [
            Input(component_id="dropdown-menu", component_property="value"),
            Input(component_id="select-date", component_property="date"),
            Input(component_id="url", component_property="pathname"),
        ],
    )
    def update_plot(value: str, date: str, pathname: str):
        log.info(f"Pathname={pathname}")
        return generate_map_region(value, date)  # , generate_plot(value)

    @app.callback(
        Output(component_id="bar-plot-overall", component_property="figure"),
        [
            Input(component_id="map-plot-italy", component_property="clickData"),
            Input(component_id="bar-plot-selected", component_property="relayoutData"),
            Input(component_id="reset-button", component_property="n_clicks"),
        ],
    )
    def update_bar_plot_overall(hoverData, relayout, n_clicks):
        ctx = dash.callback_context
        if ctx.triggered[0]["prop_id"] == "reset-button.n_clicks":
            region = "Italia"
        else:
            region = (
                [v["text"] for v in hoverData["points"]][0] if hoverData else "Italia"
            )
        fig = generate_bar_plot_overall(region)
        fig = update_xaxis(fig, relayout)
        return fig

    @app.callback(
        Output(component_id="bar-plot-selected", component_property="figure"),
        [
            Input(component_id="dropdown-menu", component_property="value"),
            Input(component_id="map-plot-italy", component_property="clickData"),
            Input(component_id="bar-plot-overall", component_property="relayoutData"),
            Input(component_id="reset-button", component_property="n_clicks"),
        ],
    )
    def update_bar_plot_selected(value: str, hoverData, relayout, n_clicks):
        ctx = dash.callback_context
        if ctx.triggered[0]["prop_id"] == "reset-button.n_clicks":
            region = "Italia"
        else:
            region = (
                [v["text"] for v in hoverData["points"]][0] if hoverData else "Italia"
            )
        fig = generate_bar_plot_selected(region=region, value=value)
        fig = update_xaxis(fig, relayout)
        return fig

    @app.callback(
        Output("modal-help", "is_open"),
        [Input("help-button", "n_clicks"), Input("close-help-button", "n_clicks")],
        [State("modal-help", "is_open")],
    )
    def toggle_modal(n1: int, n2: int, is_open: bool):
        """This callback is used to open/close the modal help form
        
        Arguments:
            n1 {int} -- help-button clicks
            n2 {int} -- close-help button clicks
            is_open {bool} -- state 
        
        Returns:
            [type] -- [description]
        """
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        [Output(f"navlink-regioni", "active"), Output("navlink-province", "active")],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/":
            # Treat page 1 as the homepage / index
            return False, False
        return [pathname == "/regioni", pathname == "/province"]
