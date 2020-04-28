import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


COUNTRIES = {
    "Italy": 60_461_826,
    "Spain": 46_754_778,
    "China (mainland)": 1_439_323_776,
    "United Kingdom": 67_886_011,
    "France": 65_273_511,
    "Germany": 83_783_942,
    "United States": 331_002_651,
    "South Korea": 51_269_185,
    "Netherlands": 17_134_872,
    "Belgium": 11_589_623,
}


VALUES = [
    "deaths",
    "confirmed",
    "recovered",
    "deaths_change",
    "confirmed_change",
    "recovered_change",
]


def get_world_layout():
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Select countries"),
                        dcc.Dropdown(
                            id="dropdown-select-countries",
                            options=[{"value": c, "label": c} for c in COUNTRIES],
                            optionHeight=30,
                            multi=True,
                            searchable=True,
                            value=list(COUNTRIES),
                        ),
                        html.H5("Select value", style={"marginTop": "15px"}),
                        dcc.Dropdown(
                            id="dropdown-select-value",
                            options=[{"value": c, "label": c} for c in VALUES],
                            optionHeight=30,
                            multi=False,
                            searchable=True,
                            value=VALUES[0],
                        ),
                        # html.H5("Relative to the population", style={"marginTop": "15px"}),
                        dcc.Checklist(
                            id="select-normalized",
                            options=[
                                {
                                    "label": "Normalize to 1 Million people",
                                    "value": "normalized",
                                }
                            ],
                            className="dcc_control",
                            value=[],
                            style={"marginTop": "10px"},
                        ),
                    ],
                    md=2,
                ),
                dbc.Col(dcc.Graph(id="world-plot")),
            ],
            style={"marginTop": "20px"},
        ),
    ]
