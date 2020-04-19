from dash import Dash
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime as dt
from typing import List, Optional
import os
import dash

import logging

from . import data  # import get_italy_map_region, get_db_region_data

log = logging.getLogger(__name__)

# cache data
conn = os.environ.get("DB_CONN", "sqlite:///covid.db")
log.info("Loading data...")
map_data_region = data.get_italy_map_region()
region_df: pd.DataFrame = data.get_db_region_data(conn)
province_df: pd.DataFrame = data.get_db_province_data(conn)
# historical_df = get_time_data()


def aggregate_province_per_region(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the province total cases by region, and set a string for the map hover
    
    Arguments:
        df {pd.DataFrame} -- Province dataframe
    
    Returns:
        pd.DataFrame -- Aggregated dataframe (rows=regions, columns=[codice_regione, tot_by_prov])
    """

    def aggregate(dfi):
        tot = dfi["denominazione_provincia"].str.cat(
            dfi["sigla_provincia"].str.cat(dfi["totale_casi"].astype(str), sep=": "),
            sep=" ",
        )
        return "<br>".join(tot)

    return (
        (df.groupby("codice_regione").apply(aggregate))
        .reset_index()
        .rename(columns={0: "tot_by_prov"})
    )


def generate_map_region(value, data: Optional[dt.date] = None) -> go.Figure:
    max_data = region_df.data.dt.date.max()
    data = (
        min(dt.datetime.strptime(data, "%Y-%m-%d").date(), max_data)
        if isinstance(data, str)
        else max_data
    )
    log.debug(f"Generating map plot for {data}..")
    # filter data for the given date
    region_day_df = region_df.loc[region_df["data"].dt.date == data, :]
    province_day_df = province_df.loc[province_df["data"].dt.date == data, :]
    aggr_province = aggregate_province_per_region(province_day_df)

    region_day_df = region_day_df.merge(aggr_province, on="codice_regione")

    cp = go.Choropleth(
        geojson=map_data_region,
        locations=region_day_df["codice_regione"],
        z=region_day_df[value],
        featureidkey="properties.reg_istat_code_num",
        colorscale="Pinkyl",
        text=region_day_df["denominazione_regione"],
        hovertemplate=(
            "<b>%{text}</b><br><br>"
            "totale positivi=%{customdata[1]}<br>"
            "dimessi_guariti=%{customdata[2]}<br>"
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
            height=800,
            width=800,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
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
        columns {list} -- List of columns to plot as stacked bar (default: {["dimessi_guariti","isolamento_domiciliare","ricoverati_con_sintomi","terapia_intensiva","deceduti",]})
    
    Returns:
        [type] -- figure
    """
    # df = get_time_data_db(columns, region=region)
    df1 = region_df[columns + ["data", "denominazione_regione"]]
    if region != "Italia":
        df1 = df1.query("denominazione_regione==@region")
    else:
        df1 = df1.groupby(["data"], as_index=False).sum()

    return go.Figure(
        data=[
            go.Bar(name=col.replace("_", " "), x=df1["data"], y=df1[col])
            for col in columns
        ],
        layout=go.Layout(
            plot_bgcolor="white",
            barmode="stack",
            legend=dict(
                x=0.02, y=0.98, title=f"<b> {region} </b>", traceorder="normal",
            ),
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


def generate_bar_plot_selected(region="Italia", value="totale_casi"):
    df1 = region_df[["data", "denominazione_regione", value]]
    if region == "Italia":
        df1 = df1.groupby(["data"], as_index=False).sum()
    else:
        df1 = df1.query("denominazione_regione==@region")

    return go.Figure(
        data=[
            go.Bar(
                name=value,
                x=df1["data"],
                y=df1[value],
                # line=go.scatter.Line(width=3)
            )
        ],
        layout=go.Layout(
            plot_bgcolor="white",
            barmode="stack",
            yaxis=go.layout.YAxis(title=value.replace("_", " ")),
            legend=dict(
                x=0.02, y=0.98, title=f"<b> {region} </b>", traceorder="normal",
            ),
            title=f"{region}: {value.replace('_', ' ')}",
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
