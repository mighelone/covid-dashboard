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

from .. import data  # import get_italy_map_region, get_db_region_data
from .. import db
from ..plots.maps import generate_map_region, generate_map_province
from ..plots.bar import (
    generate_bar_plot_overall,
    generate_bar_plot_selected,
    generate_bar_plot_provicie,
)

log = logging.getLogger(__name__)

log.info("Loading data...")

MAP_LABELS_REGION = [
    {"label": l.replace("_", " "), "value": l}
    for l in [
        "ricoverati_con_sintomi",
        "terapia_intensiva",
        "totale_ospedalizzati",
        "isolamento_domiciliare",
        "totale_positivi",
        "variazione_totale_positivi",
        "nuovi_positivi",
        "dimessi_guariti",
        "deceduti",
        "totale_casi",
        "tamponi",
        # new values
        "variazione_deceduti",
    ]
]
DEFAULT_REGION = "variazione_totale_positivi"

DEFAULT_PROVINCE = "totale_casi"
MAP_LABELS_PROVINCE = [
    {"label": DEFAULT_PROVINCE.replace("_", " "), "value": DEFAULT_PROVINCE}
]


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


def set_callbacks_italy(app: Dash):
    @app.callback(
        Output(component_id="map-plot-italy", component_property="figure"),
        [
            Input(component_id="dropdown-menu", component_property="value"),
            Input(component_id="select-date", component_property="date"),
            Input(component_id="url", component_property="pathname"),
        ],
    )
    def update_plot(value: str, date: str, pathname: str) -> go.Figure:
        """Update the map plot

        Arguments:
            date {str} -- Date of the plot
            pathname {str} -- Dashboard pathname for showing province or regioni

        Returns:
            go.Figure -- New generated figure
        """
        log.debug(f"Pathname={pathname}")
        if pathname == "/province":
            return generate_map_province("totale_casi", date)
        else:
            return generate_map_region(value, date)  # , generate_plot(value)

    @app.callback(
        Output(component_id="bar-plot-overall", component_property="figure"),
        [
            Input(component_id="map-plot-italy", component_property="clickData"),
            Input(component_id="bar-plot-selected", component_property="relayoutData"),
            Input(component_id="reset-button", component_property="n_clicks"),
        ],
        [State("url", "pathname")],
    )
    def update_bar_plot_overall(hoverData, relayout, n_clicks: int, pathname: str):
        ctx = dash.callback_context
        if ctx.triggered[0]["prop_id"] == "reset-button.n_clicks":
            region = "Italia"
        elif pathname == "/province":
            # import pdb; pdb.set_trace()
            region = (
                (
                    db.db.session.query(db.ItalyRegion.denominazione_regione)
                    .filter(
                        db.ItalyRegion.codice_regione == db.ItalyProvince.codice_regione
                    )
                    .filter(
                        db.ItalyProvince.denominazione_provincia
                        == hoverData["points"][0]["customdata"][1]
                    )
                ).first()[0]
                if hoverData
                else "Italia"
            )
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
        [State("url", "pathname")],
    )
    def update_bar_plot_selected(value: str, hoverData, relayout, n_clicks, pathname):
        ctx = dash.callback_context
        if ctx.triggered[0]["prop_id"] == "reset-button.n_clicks":
            region = "Italia"
            fig = generate_bar_plot_selected(region=region, value=value)
        elif pathname == "/province":
            region = "Italia"
            if hoverData:
                provincia = hoverData["points"][0]["customdata"][1]
                fig = generate_bar_plot_provicie(
                    provincia=provincia, value="totale_casi"
                )
            else:
                fig = generate_bar_plot_selected(region="Italia", value=value)
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

    # @app.callback(
    #     [Output(f"navlink-regioni", "active"), Output("navlink-province", "active")],
    #     [Input("url", "pathname")],
    # )
    # def toggle_active_links(pathname):
    #     if pathname == "/":
    #         # Treat page 1 as the homepage / index
    #         return False, False
    #     return [pathname == "/regioni", pathname == "/province"]

    @app.callback(
        [Output("dropdown-menu", "options"), Output("dropdown-menu", "value")],
        [Input("dropdown-visualizzazione", "value")],
    )
    def update_dropdown_menu(value: str):
        if value == "province":
            return (MAP_LABELS_PROVINCE, DEFAULT_PROVINCE)
        else:
            return (MAP_LABELS_REGION, DEFAULT_REGION)
