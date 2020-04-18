from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px

import datetime as dt


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

DEFAULT = "variazione_totale_positivi"


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
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.H6("Seleziona valore: "),
                                        align="center",
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="dropdown-menu",
                                            options=map_labels,
                                            value=DEFAULT
                                            # multi=False,
                                        ),
                                        align="center",
                                        md=4,
                                        # offset=3,
                                    ),
                                    dbc.Col(
                                        html.H6("Seleziona data: "),
                                        align="center",
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dcc.DatePickerSingle(
                                            id="select-date",
                                            date=dt.date.today(),
                                            min_date_allowed=dt.date(2020, 2, 24),
                                            max_date_allowed=dt.date.today(),
                                            stay_open_on_select=False,
                                            display_format="YYYY MM DD",
                                            # style={"marginTop": "10px"},
                                        ),
                                        md=4,
                                        align="center",
                                    ),
                                ],
                                justify="around",
                            ),
                            dbc.Row(
                                dbc.Col(dcc.Graph(id="map-plot-italy")),
                                style={"marginTop": "10px"},
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Jumbotron(
                                        [
                                            html.H5("Istruzioni"),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.P(
                                                                "Clicca su una regione per aggiornare i grafici a destra."
                                                            )
                                                        ],
                                                        className="li",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.P(
                                                                "Il valore rappresentato nella mappa puo essere cambiato selezionando un nuovo valore dal menu a tendina in alto a sinistra"
                                                            )
                                                        ],
                                                        className="li",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.P(
                                                                "Seleziona la data in alto a sinistra per mostrare il valore nella data selezionata."
                                                            )
                                                        ],
                                                        className="li",
                                                    ),
                                                ],
                                                className="ul",
                                            ),
                                        ]
                                    ),
                                    style={"marginTop": "20px"},
                                    md=10,
                                ),
                                justify="center",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(id="bar-plot-selected", figure={}),
                            dcc.Graph(id="bar-plot-overall", figure={}),
                        ],
                        md=6,
                    ),
                ],
            ),
        ],
        fluid=True,
    )
