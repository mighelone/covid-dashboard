from dash import Dash
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime as dt
from typing import List, Optional

import logging

from .data import (
    get_italy_map_region,
    get_time_data_db,
    get_total_data_db,
    get_db_data
)

log = logging.getLogger(__name__)

# cache data
log.info("Loading data...")
map_data = get_italy_map_region()
df: pd.DataFrame = get_db_data()
# historical_df = get_time_data()


def generate_choropleth(value, data: Optional[dt.date]=None):
    if isinstance(data, str):
        data = dt.datetime.strptime(data, '%Y-%m-%d').date()
    elif data is None: 
        data = dt.date.today()
    df1 = df.loc[df['data'].dt.date == data, :]
    fig = px.choropleth_mapbox(
        df1,
        geojson=map_data,
        # locations="codice_regione",
        locations="codice_regione",
        # color="terapia_intensiva",
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
        zoom=4.7,
        title=value.replace("_", ""),
        mapbox_style="carto-positron",
        # projection="equirectangular",
        color_continuous_scale="Pinkyl",
        # range_color=(0, 12),
        # scope="europe",
        # labels={"value": "something"},
        # width=900,
        height=600,
    )
    # fig.update_geos(fitbounds="locations", visible=False, overwrite=True)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def generate_bar_plot_time(
    region: str = "Italy",
    columns: List[str]=[
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
    df1 = df[columns+['data', 'denominazione_regione']]
    if region != "Italia":
        df1 = df1.query("denominazione_regione==@region")
    else:
        df1 = df1.groupby(['data'], as_index=False).sum()

    return go.Figure(
        data=[
            go.Bar(name=col.replace('_', ' '), x=df1['data'], y=df1[col])
            for col in columns
        ],
        layout=go.Layout(
            plot_bgcolor='white',
            barmode='stack',
            legend=dict(
                x=0.02,
                y=0.98,
                title=f'<b> {region} </b>',
                traceorder="normal",
            )
        )
                    
    )

def generate_bar_plot_new_positives(region='Italia'):
    df1 = df[['data', 'denominazione_regione', 'variazione_totale_positivi']]
    if region == 'Italia':
        df1 = df1.groupby(['data'], as_index=False).sum()
    else:
        df1 = df1.query("denominazione_regione==@region")
    return go.Figure(
        data=[
            go.Bar(name='', x=df1['data'], y=df1['variazione_totale_positivi'])
        ],
        layout=go.Layout(
            plot_bgcolor='white',
            barmode='stack',
            legend=dict(
                x=0.02,
                y=0.98,
                title=f'<b> {region} </b>',
                traceorder="normal",
            )
        )
                    
    )


def set_callbacks(app: Dash):
    @app.callback(
        Output(component_id="italy-plot", component_property="figure"),
        [
            Input(component_id="dropdown-menu", component_property="value"),
            Input(component_id="select-date", component_property="date")
        ],
    )
    def update_plot(value, date):
        return generate_choropleth(value, date)  # , generate_plot(value)


    @app.callback(
        [
            Output(component_id='bar_plot_time', component_property='figure'),
            Output(component_id='bar_plot_new_positives', component_property='figure'),
        ],
        [Input(component_id='dropdown-region', component_property='value')]
    )
    def update_bar_plot_time(value):
        return generate_bar_plot_time(value), generate_bar_plot_new_positives(value)
    