from dash import Dash
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

import logging

from .data import (
    get_italy_map_region,
    get_italy_regional_data,
    get_time_data_db,
    get_total_data_db,
)

log = logging.getLogger(__name__)

# cache data
log.info("Loading data...")
map_data = get_italy_map_region()
df = get_italy_regional_data()
# historical_df = get_time_data()


def generate_choropleth(value):
    fig = px.choropleth_mapbox(
        df,
        geojson=map_data,
        # locations="codice_regione",
        locations="codice_regione",
        # color="terapia_intensiva",
        color=value,
        center={"lon": 12, "lat": 42},
        featureidkey="properties.reg_istat_code",
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


def generate_plot(value="totale_positivi"):
    historical_df = get_time_data_db(value)

    lines = [
        go.Scatter(
            x=dfi["data"],
            y=dfi[value],
            #         title='totale',
            line={"width": 3},
            name=key,
        )
        for key, dfi in historical_df.groupby("denominazione_regione")
    ]
    fig = go.Figure(
        data=lines,
        layout=go.Layout(
            xaxis_title="Day",
            yaxis_title=value.replace("_", ""),
            plot_bgcolor="white",
            legend_orientation="h",
            height=800,
        ),
    )
    return fig


def generate_total_plot(columns=["totale_casi", "deceduti", "dimessi_guariti"]):
    columns = [columns] if isinstance(columns, str) else columns
    df = get_total_data_db(columns)
    df = df.melt(id_vars="data", value_vars=columns)
    fig = px.line(df, x="data", y="value", color="variable", width=800)
    fig.update_layout(
        plot_bgcolor="white",
        # yaxis_type='log'
    )
    return fig


def generate_bar_plot_time(
    region: str = "Italy",
    columns=[
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
    df = get_time_data_db(columns, region=region)

    return go.Figure(
        data=[
            go.Bar(name=col.replace('_', ' '), x=df['data'], y=df[col])
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

def set_callbacks(app: Dash):
    @app.callback(
        Output(component_id="italy-plot", component_property="figure"),
        [Input(component_id="dropdown-menu", component_property="value")],
    )
    def update_plot(value):
        return generate_choropleth(value)  # , generate_plot(value)


    @app.callback(
        Output(component_id='bar_plot_time', component_property='figure'),
        [Input(component_id='dropdown-region', component_property='value')]
    )
    def update_bar_plot_time(value):
        return generate_bar_plot_time(value)

    # @app.callback(
    #     Output(component_id="total-plot-2", component_property="figure"),
    #     [Input(component_id="dropdown-menu-2", component_property="value")],
    # )
    # def update_plot_2(values):
    #     return generate_total_plot(values) if values else {}
    # @app.callback()
