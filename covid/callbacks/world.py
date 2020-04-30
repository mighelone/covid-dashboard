import logging
from typing import List

import pandas as pd
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Input, Output, State
from sqlalchemy import func

from .. import db

log = logging.getLogger(__name__)

# TODO add more countries -> find a good source and match names between the 2 datasets
"""Population of main countries """
COUNTRIES = {
    "Italy": 60_461_826,
    "Spain": 46_754_778,
    "China": 1_439_323_776,
    "United Kingdom": 67_886_011,
    "France": 65_273_511,
    "Germany": 83_783_942,
    "USA": 331_002_651,
    "South Korea": 51_269_185,
    "Netherlands": 17_134_872,
    "Belgium": 11_589_623,
}


"""Threasohod values for plots showing the number of days of the epidemy"""
THREASHOLD = {
    "deaths": {"absolute": 10, "normalized": 1},
    "confirmed": {"absolute": 100, "normalized": 10},
    "recovered": {"absolute": 10, "normalized": 1},
}

""" Update menu layout component. Select Y axis log/linear"""
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
    """Set the callbacks for the world page

    Arguments:
        app {Dash} -- Dash app, the callbacks are assigned to the app
    """

    @app.callback(
        Output("world-plot", "figure"),
        [
            Input("dropdown-select-countries", "value"),
            Input("dropdown-select-value", "value"),
            Input("select-normalized", "value"),
        ],
        [State("world-plot", "figure")],
    )
    def plot_countries(
        countries: List[str], value: str, normalized: str, fig: go.Figure
    ) -> go.Figure:
        """Line plot of the selected value for the selected countries

        Arguments:
            countries {List[str]} -- List of selected countries to show
            value {str} -- Value shown on the Y-axis
            normalized {str} -- Show lines normalized per 1M of population
            fig {go.Figure} -- Old figure

        Returns:
            go.Figure -- Plotly figure object
        """
        normalized = normalized != []

        title = f"{value}" + ("/1M people" if normalized else "")

        countries = [countries] if isinstance(countries, str) else countries

        rolling = 7 if value.endswith("_change") else None

        threashold = THREASHOLD[value.replace("_change", "")][
            "normalized" if normalized else "absolute"
        ]
        # TODO normalize only works for countries with defined population. Update to all
        lines = [
            get_line(value, country, threashold, normalized, rolling)
            for country in countries
            if not normalized or country in COUNTRIES
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
    normalize=1,
    threashold: int = 100,
    rolling_average=None,
    session=None,
):

    session = session or db.db.session
    query = (
        session.query(
            db.WorldCase.date, func.sum(db.WorldCase.__table__.c[value]).label(value)
        )
        .filter(db.WorldCase.country == country)
        .group_by(db.WorldCase.date)
        .order_by(db.WorldCase.date)
    )
    df = pd.DataFrame(query)
    if rolling_average:
        df[value] = df[value].rolling(rolling_average, min_periods=1).mean()

    if normalize != 1:
        df[value] = df[value].astype(int) / normalize
    df = df[df[value] > threashold]
    return df


def get_line(value: str, country: str, threashold: int, normalized: bool, rolling: int):
    df = get_data(
        value,
        country,
        threashold=threashold,
        normalize=COUNTRIES[country] / 1e6 if normalized else 1,
        rolling_average=rolling,
    )
    return go.Scatter(
        y=df[value],
        text=df["date"],
        name=country,
        line=go.scatter.Line(width=3),
        hovertemplate=(
            f"<b>{country}<b><br>" + value + ": %{y}<br>" + "days: %{x}<br>"
            "Date: %{text}"
        ),
    )
