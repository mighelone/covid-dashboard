from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px

from .callbacks import generate_choropleth, generate_plot, generate_total_plot

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


# def set_layout(app: Dash):
#     dropdown_menu = dcc.Dropdown(
#         id="dropdown-menu",
#         options=map_labels,
#         value=map_labels[0]["value"],
#         multi=False,
#     )
def set_layout(app: Dash):
    navbar = dbc.NavbarSimple(
        # children=[
        #     # dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        #     dbc.DropdownMenu(
        #         children=[
        #             dbc.DropdownMenuItem("More pages", header=True),
        #             dbc.DropdownMenuItem("Page 2", href="#"),
        #             dbc.DropdownMenuItem("Page 3", href="#"),
        #         ],
        #         nav=True,
        #         in_navbar=True,
        #         label="More",
        #     ),
        # ],
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
                        dcc.Dropdown(
                            id="dropdown-menu",
                            options=map_labels,
                            value=DEFAULT
                            # multi=False,
                        ),
                        # align='center',
                        width={"size": 2},
                    ),
                    dbc.Col(dcc.Graph(id="italy-plot")),
                ]
            ),
            html.Div(style={"padding": 10}),
            #
            dbc.Row(dbc.Col(dcc.Graph(id="bar_plot_time", figure={}))),
            dbc.Row(
                [
                    dbc.Col([html.H5("Seleziona regione")], width={"size": 2}),
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id="dropdown-region",
                                options=map_regions,
                                value="Italia"
                                # multi=False,
                            ),
                        ],
                        width={"size": 2},
                    ),
                ]
            ),
        ]
    )
