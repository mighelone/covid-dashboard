from dash import Dash
from dash.dependencies import Input, Output
import plotly.express as px


from .data import get_italy_map_region, get_italy_regional_data

map_data = get_italy_map_region()
df = get_italy_regional_data()


def set_callbacks(app: Dash):
    @app.callback(
        Output(component_id="italy-plot", component_property="figure"),
        [Input(component_id="dropdown-menu", component_property="value")],
    )
    def update_plot(value):
        fig = px.choropleth(
            df,
            geojson=map_data,
            # locations="codice_regione",
            locations="codice_regione",
            # color="terapia_intensiva",
            color=value,
            featureidkey="properties.reg_istat_code",
            color_continuous_scale="Viridis",
            # range_color=(0, 12),
            # scope="europe",
            # labels={"value": "something"},
        )
        fig.update_geos(fitbounds="locations", visible=False, overwrite=True)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig
