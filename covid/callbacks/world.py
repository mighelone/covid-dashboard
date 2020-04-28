from typing import List
from dash import Dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import logging

from .. import db

db.WorldCase.deaths_change

log = logging.getLogger(__name__)

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

THREASHOLD = {
    "deaths": {"absolute": 10, "normalized": 1},
    "confirmed": {"absolute": 100, "normalized": 10},
    "recovered": {"absolute": 10, "normalized": 1},
}

updatemenu = go.layout.Updatemenu(
    type="buttons",
    active=1,
    buttons=[
        go.layout.updatemenu.Button(
            label="Log", method="relayout", args=[{"yaxis.type": "log"}]
        ),
        go.layout.updatemenu.Button(
            label="Linear", method="relayout", args=[{"yaxis.type": "linear",}]
        ),
    ],
)


def set_callbacks_world(app: Dash):
    @app.callback(
        Output("world-plot", "figure"),
        [
            Input("dropdown-select-countries", "value"),
            Input("dropdown-select-value", "value"),
            Input("select-normalized", "value"),
        ],
    )
    def plot_countries(countries: List[str], value: str, normalized: str):

        normalized = normalized != []

        title = f"{value}" + ("/1M people" if normalized else "")

        countries = [countries] if isinstance(countries, str) else countries

        rolling = 7 if value.endswith("_change") else None

        threashold = THREASHOLD[value.replace("_change", "")][
            "normalized" if normalized else "absolute"
        ]
        lines = [
            get_line(value, country, threashold, normalized, rolling)
            for country in countries
        ]
        layout = go.Layout(
            template="plotly_white",
            yaxis=go.layout.YAxis(title=f"{value}",),
            updatemenus=[updatemenu],
            height=800,
            xaxis=go.layout.XAxis(title="Days"),
            title=title,
            legend=go.layout.Legend(x=0.02, y=0.98),
        )

        return go.Figure(data=lines, layout=layout)


def get_data(
    value,
    country,
    adm1="",
    adm2="",
    normalize=1,
    threashold: int = 100,
    rolling_average=None,
    session=None,
):

    session = session or db.db.session
    query = (
        session.query(db.WorldCase.updated, db.WorldCase.__table__.c[value])
        .filter(db.WorldCase.country_region == country)
        .filter(db.WorldCase.admin_region_1 == adm1)
        .filter(db.WorldCase.admin_region_2 == adm2)
        .order_by(db.WorldCase.updated)
        .all()
    )
    df = pd.DataFrame(query)
    if rolling_average:
        df[value] = df[value].rolling(rolling_average, min_periods=1).mean()

    df[value] = df[value] / normalize
    df = df[df[value] > threashold]
    return df


def get_line(value: str, country: str, threashold: int, normalized: bool, rolling: int):
    # import pdb; pdb.set_trace()
    df = get_data(
        value,
        country,
        threashold=threashold,
        normalize=COUNTRIES[country] / 1e6 if normalized else 1,
        rolling_average=rolling,
    )
    return go.Scatter(
        y=df[value],
        text=df["updated"],
        name=country,
        line=go.scatter.Line(width=3),
        hovertemplate=(
            f"<b>{country}<b><br>" + value + ": %{y}<br>" + "days: %{x}<br>"
            "Date: %{text}"
        ),
    )
