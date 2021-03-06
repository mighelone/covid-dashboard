import logging
from typing import Any, Dict, List

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Dash
from sqlalchemy import func
from dash.dependencies import Input, State, Output

from ... import db
from ...data import get_population_data

log = logging.getLogger(__name__)

"""Population of main countries """
COUNTRIES = get_population_data()


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
            label="Linear", method="relayout", args=[{"yaxis.type": "linear"}]
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
        rolling = 7 if value.endswith("_change") else None

        threashold = THREASHOLD[value.replace("_change", "")][
            "normalized" if normalized else "absolute"
        ]
        ctx = dash.callback_context
        log.debug(f"Plot Triggered {ctx.triggered}")
        # check if the plot needs only to be updated
        if ctx.triggered[0]["prop_id"] == "dropdown-select-countries.value" and fig:
            return update_lines(
                fig=fig,
                value=value,
                countries=countries,
                threashold=threashold,
                rolling=rolling,
                normalized=normalized,
            )

        title = f"{value}" + ("/1M people" if normalized else "")
        countries = [countries] if isinstance(countries, str) else countries

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
    value: str,
    country: str,
    normalize: int = 1,
    threashold: int = 100,
    rolling_average=None,
    session=None,
):

    session = session or db.db.session
    change = value.endswith("_change")
    value_query = value.replace("_change", "")
    query = (
        session.query(
            db.WorldCase.date,
            func.sum(db.WorldCase.__table__.c[value_query]).label(value),
        )
        .filter(db.WorldCase.country == country)
        .group_by(db.WorldCase.date)
        .order_by(db.WorldCase.date)
    )
    df = pd.DataFrame(query)
    if change:
        df[value] = df[value].diff()
    if rolling_average:
        df[value] = df[value].rolling(rolling_average, min_periods=1).mean()

    if normalize != 1:
        df[value] = df[value].astype(float) / normalize
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
            f"<b>{country}<b><br>" + value + ": %{y:.0f}<br>" + "days: %{x}<br>"
            "Date: %{text}"
        ),
    )


def update_lines(
    fig: go.Figure,
    value: str,
    countries: List[str],
    threashold: float,
    rolling: bool,
    normalized: bool,
) -> Dict[str, Any]:
    log.debug("Plot Triggered by new countries selection")
    old_countries = set([d["name"] for d in fig["data"]])
    log.debug(f"Old countries = {old_countries}")
    countries_set = set(countries)
    removed_countries = old_countries - countries_set
    added_countries = countries_set - old_countries
    log.debug(f"Add new countries: {added_countries}")
    log.debug(f"Remove old countries: {removed_countries}")
    if removed_countries:
        new_data = [
            line for line in fig["data"] if line["name"] not in removed_countries
        ]
        fig["data"] = new_data
        log.debug("Updated fig removing countries")
    if added_countries:
        new_lines = [
            get_line(value, country, threashold, normalized, rolling).to_plotly_json()
            for country in added_countries
            if not normalized or country in COUNTRIES
        ]
        log.debug("Updated fig adding new countries")
        fig["data"].extend(new_lines)

    return fig
