from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px

import datetime as dt

from .callbacks import generate_plot_region


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

map_regions = [
    {"label": l.replace("_", " "), "value": l}
    for l in [
        "Italia",
        "Piemonte",
        "Valle d'Aosta",
        "Lombardia",
        "Veneto",
        "Friuli Venezia Giulia",
        "Liguria",
        "Trentino Alto Adige",
        "Toscana",
        "Umbria",
        "Marche",
        "Lazio",
        "Abruzzo",
        "Molise",
        "Campania",
        "Puglia",
        "Basilicata",
        "Calabria",
        "Sicilia",
        "Sardegna",
    ]
]

DEFAULT = "totale_casi"


def set_layout(app: Dash):
    navbar = dbc.NavbarSimple(
        brand="COVID-19 dashboard",
        brand_href="#",
        # color="primary",
        color="dark",
        dark=True,
    )
    app.layout = dbc.Container(
        [
            navbar,
            html.Div(style={"padding": 10}),
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
                            dcc.DatePickerSingle(
                                id="select-date",
                                date=dt.date.today(),
                                min_date_allowed=dt.date(2020, 2, 24),
                                max_date_allowed=dt.date.today(),
                                style={"marginTop": "10px"},
                            ),
                        ],
                        # align='center',
                        width={"size": 2},
                    ),
                    dbc.Col(dcc.Graph(id="italy-plot")),
                ]
            ),
            dbc.Row(dbc.Col(dcc.Graph(id="region-line", figure={}))),
            # html.Div(style={"padding": 10}),
            #
            # dbc.Row(html.Hr()),
            # dbc.Row(
            #     [
            #         dbc.Col([html.H5("Seleziona regione")], width={"size": 2}),
            #         dbc.Col(
            #             [
            #                 dcc.Dropdown(
            #                     id="dropdown-region",
            #                     options=map_regions,
            #                     value="Italia"
            #                     # multi=False,
            #                 ),
            #             ],
            #             width={"size": 4},
            #         ),
            #     ]
            # ),
            dbc.Row(
                dbc.Col(dcc.Graph(id="bar_plot_time", figure={})),
                style={"marginTop": "20px"},
            ),
            # dbc.Row(
            #     dbc.Col(dcc.Graph(id="bar_plot_new_positives", figure={})),
            #     style={"marginTop": "20px"},
            # ),
        ]
    )
