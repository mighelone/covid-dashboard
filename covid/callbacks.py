from dash import Dash
from dash.dependencies import Input, Output, State
import plotly.express as px
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

log = logging.getLogger(__name__)

log.info("Loading data...")
map_data_region = data.get_italy_map_region()


def generate_map_region(value: str, data: Optional[dt.date] = None) -> go.Figure:
    """Generate the map region for the given data showing the given value
    
    Arguments:
        value {str} -- Value to visualize
    
    Keyword Arguments:
        data {Optional[dt.date]} -- Date to visualize (default: {None})
    
    Returns:
        go.Figure -- [description]
    """
    value = "deceduti" if value == "variazione_deceduti" else value
    session = db.db.session
    max_data = session.query(func.max(db.ItalyRegionCase.data)).first()[0]
    # max_data = region_df.data.dt.date.max()
    data = (
        min(dt.datetime.strptime(data, "%Y-%m-%d").date(), max_data)
        if isinstance(data, str)
        else max_data
    )

    concat = func.CONCAT(
        db.ItalyProvince.denominazione_provincia,
        " (",
        db.ItalyProvince.sigla_provincia,
        "): ",
        db.ItalyProvinceCase.totale_casi,
    )  # .label('provincia'),

    sub_query = (
        session.query(
            db.ItalyProvince.codice_regione,
            func.GROUP_CONCAT(concat, "<br>").label("tot_by_prov"),
        )
        .filter(
            db.ItalyProvince.codice_provincia == db.ItalyProvinceCase.codice_provincia
        )
        .filter(db.ItalyProvinceCase.data == data)
        .filter(db.ItalyProvince.codice_provincia < 200)
        .group_by(db.ItalyProvince.codice_regione)
    ).subquery()

    columns = ["totale_positivi", "dimessi_guariti", "deceduti"]

    select_columns = set(columns + [value])

    query = (
        session.query(
            db.ItalyRegion.codice_regione,
            db.ItalyRegion.denominazione_regione,
            *[db.ItalyRegionCase.__table__.columns[col] for col in select_columns],
            sub_query.c.tot_by_prov,
        )
        .filter(db.ItalyRegion.codice_regione == sub_query.c.codice_regione)
        .filter(db.ItalyRegionCase.data == data)
        .filter(db.ItalyRegionCase.codice_regione == db.ItalyRegion.codice_regione)
    )
    region_day_df = pd.DataFrame(query)

    log.debug(f"Generating map plot for {data}..")
    # filter data for the given date
    # region_day_df = region_df.loc[region_df["data"].dt.date == data, :]
    # province_day_df = province_df.loc[province_df["data"].dt.date == data, :]
    # aggr_province = aggregate_province_per_region(province_day_df)

    # region_day_df = region_day_df.merge(aggr_province, on="codice_regione")

    cp = go.Choropleth(
        geojson=map_data_region,
        locations=region_day_df["codice_regione"],
        z=region_day_df[value],
        featureidkey="properties.reg_istat_code_num",
        colorscale="Pinkyl",
        text=region_day_df["denominazione_regione"],
        hovertemplate=(
            "<b>%{text}</b><br><br>" + value + "=%{z}<br>"
            "totale positivi=%{customdata[1]}<br>"
            "dimessi guariti=%{customdata[2]}<br>"
            "deceduti=%{customdata[3]}<br><br>"
            "<b>Totale per provincie</b>:<br>"
            "%{customdata[0]}"
            "<extra></extra>"
        ),
        customdata=region_day_df[
            ["tot_by_prov", "totale_positivi", "dimessi_guariti", "deceduti",]
        ],
    )

    fig = go.Figure(
        data=cp,
        layout=go.Layout(
            geo=go.layout.Geo(
                fitbounds="locations", visible=False, projection={"type": "mercator"}
            ),
            title=go.layout.Title(
                text=f"Distribuzione {value.replace('_', ' ')} {data:%Y-%m-%d}"
            ),
            height=800,
            # width=800,
            # margin={"r": 0, "t": 0, "l": 0, "b": 0},
        ),
    )
    return fig


def generate_bar_plot_overall(
    region: str = "Italy",
    columns: List[str] = [
        "dimessi_guariti",
        "isolamento_domiciliare",
        "ricoverati_con_sintomi",
        "terapia_intensiva",
        "deceduti",
    ],
):
    """Generate a stacked bar plot of the given columns for a region or for the whole country
    
    Keyword Arguments:
        region {str} -- Region to visualize (default: {"Italy"})
        columns {list} -- List of columns to plot as stacked bar (default: {["dimessi_guariti","isolamento_domiciliare","ricoverati_con_sintomi",
            "terapia_intensiva","deceduti",]})
    
    Returns:
        [type] -- figure
    """

    if region != "Italia":
        # df1 = df1.query("denominazione_regione==@region")
        query = (
            db.db.session.query(
                db.ItalyRegion.codice_regione,
                db.ItalyRegion.denominazione_regione,
                db.ItalyRegionCase.data,
                *[db.ItalyRegionCase.__table__.columns[col] for col in columns],
            )
            .filter(db.ItalyRegionCase.codice_regione == db.ItalyRegion.codice_regione)
            .filter(db.ItalyRegion.denominazione_regione == region)
        )
        df1 = pd.DataFrame(query)
    else:
        # df1 = df1.groupby(["data"], as_index=False).sum()
        query = db.db.session.query(
            db.ItalyRegionCase.data,
            *[
                func.sum(db.ItalyRegionCase.__table__.columns[col]).label(col)
                for col in columns
            ],
        ).group_by(db.ItalyRegionCase.data)
        df1 = pd.DataFrame(query)

    x = df1["data"]
    return go.Figure(
        data=[go.Bar(name=col.replace("_", " "), x=x, y=df1[col]) for col in columns],
        layout=go.Layout(
            plot_bgcolor="white",
            barmode="stack",
            legend=dict(
                x=0.02, y=0.98,  # title=f"<b> {region} </b>", traceorder="normal",
            ),
            title=f"{region}: andamento casi",
            height=400,
        ),
    )


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


def generate_bar_plot_selected(region="Italia", value: str = "totale_casi"):
    value_query, do_increment = (
        ("deceduti", True) if value == "variazione_deceduti" else (value, False)
    )

    if region == "Italia":
        query = (
            db.db.session.query(
                db.ItalyRegionCase.data,
                func.sum(db.ItalyRegionCase.__table__.columns[value_query]).label(
                    value_query
                ),
            )
            .filter(db.ItalyRegion.codice_regione == db.ItalyRegionCase.codice_regione)
            .group_by(db.ItalyRegionCase.data)
        )
    else:
        query = (
            db.db.session.query(
                db.ItalyRegionCase.data,
                db.ItalyRegionCase.__table__.columns[value_query],
            )
            .filter(db.ItalyRegion.codice_regione == db.ItalyRegionCase.codice_regione)
            .filter(db.ItalyRegion.denominazione_regione == region)
        )

    df1 = pd.DataFrame(query)

    if do_increment:
        # import pdb; pdb.set_trace()
        df1 = df1.assign(**{value: df1[value_query].diff()})

    return go.Figure(
        data=[
            go.Bar(
                name=value.replace("_", " "),
                x=df1["data"],
                y=df1[value],
                # line=go.scatter.Line(width=3)
            )
        ],
        layout=go.Layout(
            plot_bgcolor="white",
            barmode="stack",
            # yaxis=go.layout.YAxis(title=value.replace("_", " ")),
            legend=dict(
                x=0.02, y=0.98, title=f"<b> {region} </b>", traceorder="normal",
            ),
            title=f"{region}: {value.replace('_', ' ')}",
            height=400,
        ),
    )


def set_callbacks(app: Dash):
    @app.callback(
        Output(component_id="map-plot-italy", component_property="figure"),
        [
            Input(component_id="dropdown-menu", component_property="value"),
            Input(component_id="select-date", component_property="date"),
        ],
    )
    def update_plot(value, date):
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
        if n1 or n2:
            return not is_open
        return is_open
