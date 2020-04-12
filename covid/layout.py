from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px

from .callbacks import generate_choropleth, generate_plot

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

DEFAULT = "totale_casi"


# def set_layout(app: Dash):
#     dropdown_menu = dcc.Dropdown(
#         id="dropdown-menu",
#         options=map_labels,
#         value=map_labels[0]["value"],
#         multi=False,
#     )
def set_layout(app: Dash):
    app.layout = dbc.Container(
        [
            html.H1("Italy COVID-19 dasboard"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id="dropdown-menu",
                                options=map_labels,
                                value=DEFAULT
                                # multi=False,
                            ),
                            dcc.Graph(
                                id="italy-plot", figure=generate_choropleth(DEFAULT)
                            ),
                        ],
                        # align="center",
                        width={'size': 6}
                        # width={"size": 6, "offset": 0},
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="line-plot",
                                figure=generate_plot()
                                ),
                        ],
                        # align="center",
                        width={'size': 6}
                        # width={"size": 6, "offset": 0},
                    )
                ],
            ),
        ]
    )