from dash import Dash
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime as dt
from typing import List, Optional

import logging

from .data import get_italy_map_region, get_time_data_db, get_total_data_db, get_db_data

log = logging.getLogger(__name__)

# cache data
log.info("Loading data...")
map_data = get_italy_map_region()
df: pd.DataFrame = get_db_data()
# historical_df = get_time_data()


def generate_choropleth(value, data: Optional[dt.date] = None):
    max_data = df.data.dt.date.max()
    data = (
        min(dt.datetime.strptime(data, "%Y-%m-%d").date(), max_data)
        if isinstance(data, str)
        else max_data
    )
    log.debug(f"Generating map plot for {data}..")
    df1 = df.loc[df["data"].dt.date == data, :]
    fig = px.choropleth(
        df1,
        geojson=map_data,
        locations="codice_regione",
        color=value,
        center={"lon": 12, "lat": 42},
        featureidkey="properties.reg_istat_code_num",
        hover_name="denominazione_regione",
        hover_data=[
            # "ricoverati_con_sintomi",
            # "terapia_intensiva",
            # "totale_ospedalizzati",
            # "isolamento_domiciliare",
            "totale_positivi",
            # "variazione_totale_positivi",
            # "nuovi_positivi",
            "dimessi_guariti",
            "deceduti",
            # "totale_casi",
            # "tamponi",
        ],
        title=value.replace("_", ""),
        projection="mercator",
        color_continuous_scale="Pinkyl",
        height=600,
        width=700,
        template="plotly_white",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},)
    fig.layout.coloraxis.colorbar.update(x=0)
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
    df1 = df[columns + ["data", "denominazione_regione"]]
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
    df1 = df[["data", "denominazione_regione", value]]
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
        return generate_choropleth(value, date)  # , generate_plot(value)

    @app.callback(
        Output(component_id="bar-plot-overall", component_property="figure"),
        [
            Input(component_id="map-plot-italy", component_property="hoverData"),
            Input(component_id="bar-plot-selected", component_property="relayoutData"),
        ],
    )
    def update_bar_plot_overall(hoverData, relayout):
        region = (
            [v["hovertext"] for v in hoverData["points"]][0] if hoverData else "Italia"
        )
        fig = generate_bar_plot_overall(region)
        fig = update_xaxis(fig, relayout)
        return fig

    @app.callback(
        Output(component_id="bar-plot-selected", component_property="figure"),
        [
            Input(component_id="dropdown-menu", component_property="value"),
            Input(component_id="map-plot-italy", component_property="hoverData"),
            Input(component_id="bar-plot-overall", component_property="relayoutData"),
        ],
    )
    def update_bar_plot_selected(value: str, hoverData, relayout):
        region = (
            [v["hovertext"] for v in hoverData["points"]][0] if hoverData else "Italia"
        )
        fig = generate_bar_plot_selected(region=region, value=value)
        fig = update_xaxis(fig, relayout)
        return fig
