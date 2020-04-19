from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

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

    dropdown = dbc.DropdownMenu(
        children=[
            dbc.DropdownMenuItem(
                dbc.NavLink(
                    "Dati",
                    href="https://github.com/pcm-dpc/COVID-19",
                    style={"color": "black"},
                )
            ),
            dbc.DropdownMenuItem(
                dbc.NavLink(
                    "Mappa",
                    href="https://github.com/openpolis/geojson-italy",
                    style={"color": "black"},
                )
            ),
            # dbc.DropdownMenuItem(divider=True),
            # dbc.DropdownMenuItem("Entry 3"),
        ],
        nav=True,
        in_navbar=True,
        label="Links",
    )
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            # dbc.Col(
                            #     html.Img(
                            #         src=app.get_asset_url("stayhome.jpeg"),
                            #         height="80px",
                            #     )
                            # ),
                            dbc.Col(
                                dbc.NavbarBrand("COVID-19 Dashboard", className="ml-2")
                            ),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                    # href="https://plot.ly",
                ),
                dbc.NavbarToggler(id="navbar-toggler2"),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            # dbc.NavItem(
                            #     dbc.NavLink(
                            #         "Dati", href="https://github.com/pcm-dpc/COVID-19"
                            #     )
                            # ),
                            dropdown,
                        ],
                        className="ml-auto",
                        navbar=True,
                    ),
                    id="navbar-collapse2",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        className="mb-5 navbar-expand",
        color="dark",
        dark=True,
        sticky="top",
        expand=True,
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
                                            display_format="YYYY-MM-DD",
                                        ),
                                        md=3,
                                        align="center",
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Italia",
                                            id="reset-button",
                                            # color="primary",
                                            className="mr-2",
                                        ),
                                        md=1,
                                    ),
                                ],
                                justify="around",
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dcc.Loading(
                                        dcc.Graph(
                                            id="map-plot-italy",
                                            # figure=go.Figure(data={}, layout={'height': 800})
                                        )
                                    )
                                ),
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
                            dcc.Loading(dcc.Graph(id="bar-plot-selected", figure={})),
                            dcc.Loading(dcc.Graph(id="bar-plot-overall", figure={})),
                        ],
                        md=6,
                    ),
                ],
            ),
        ],
        fluid=True,
    )
