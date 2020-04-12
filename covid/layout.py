from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


map_labels = [
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
    ]
]



def set_layout(app: Dash):
    dropdown_menu = dcc.Dropdown(
        id="dropdown-menu",
        options=map_labels,
        value=map_labels[0]["value"],
        multi=False,
    )

    app.layout = html.Div(
        children=[
            html.H1(children="Covid"),
            html.Div(
                children="""
                Dash: A web application framework for Python.
            """
            ),
            dropdown_menu,
            dcc.Graph(id="italy-plot", figure={}),
        ]
    )
