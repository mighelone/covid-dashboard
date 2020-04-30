import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from sqlalchemy import func

from .. import db

VALUES = [
    "deaths",
    "confirmed",
    "recovered",
    "deaths_change",
    "confirmed_change",
    "recovered_change",
]


def get_world_layout():
    # COUNTRIES = [c[0] for c in db.db.session.query(db.WorldCase.country.distinct()).all()]
    COUNTRIES = [
        c[0]
        for c in db.db.session.query(db.WorldCase.country)
        .group_by(db.WorldCase.country)
        .order_by(func.max(db.WorldCase.confirmed).desc())
        .all()
    ]
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
                            value=COUNTRIES[:10],
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
