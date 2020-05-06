import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def get_control_row():
    return dbc.Row(
        [
            dbc.Col(html.H6("Visualizzazione"), md=1, lg=1),
            dbc.Col(
                # html.H6("Seleziona valore"),
                dcc.Dropdown(
                    id="dropdown-visualizzazione",
                    options=[
                        {"label": "Regioni", "value": "regioni"},
                        {"label": "Province", "value": "province"},
                    ],
                    value="regioni",
                    # optionHeight='30px'
                    style={"height": "45px", "verticalAlign": "middle"},
                    searchable=False,
                    # xl=4,
                    # md=4,
                ),
                md=1,
                lg=1,
            ),
            dbc.Col(
                html.H6("Seleziona valore", style={"textAlign": "right"}), md=1, lg=1
            ),
            dbc.Col(
                # html.H6("Seleziona valore"),
                dcc.Dropdown(
                    id="dropdown-menu",
                    # options=map_labels,
                    # value=default_value,
                    # optionHeight='30px'
                    style={"height": "45px", "verticalAlign": "middle"},
                    # xl=4,
                    # md=4,
                ),
                md=2,
                lg=3,
            ),
            dbc.Col(
                html.H6("Seleziona data", style={"textAlign": "right"}), md=1, lg=1
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
                md=2,
                lg=2,
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
        align="center",
        justify="center",
        # no_gutters=True,
        style={"marginTop": "20px"},
    )
