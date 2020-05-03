import datetime as dt
import logging
from typing import List, Optional, Union

import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import func
from sqlalchemy.orm import Session

from ... import data, db

COLORSCALE = "Pinkyl"

GEO_LAYOUT = go.layout.Geo(
    fitbounds="locations", visible=False, projection={"type": "mercator"}
)
HEIGHT = 800

DataType = Optional[Union[dt.datetime, str]]

log = logging.getLogger(__name__)

map_data_region = data.get_italy_map(selection="regions")
map_data_province = data.get_italy_map(selection="provinces")

concat = func.CONCAT(
    db.ItalyProvince.denominazione_provincia,
    " (",
    db.ItalyProvince.sigla_provincia,
    "): ",
    db.ItalyProvinceCase.totale_casi,
)


def generate_map_region(value: str, data: DataType = None) -> go.Figure:
    """Generate the map region for the given data showing the given value
    
    Arguments:
        value {str} -- Value to visualize
    
    Keyword Arguments:
        data {Optional[dt.date]} -- Date to visualize (default: {None})
    
    Returns:
        go.Figure -- [description]
    """
    data = parse_data(data)
    region_day_df = get_region_data(value, data)
    log.debug(f"Generating map plot for {data}..")
    cp = go.Choropleth(
        geojson=map_data_region,
        locations=region_day_df["codice_regione"],
        z=region_day_df[value],
        featureidkey="properties.reg_istat_code_num",
        colorscale=COLORSCALE,
        text=region_day_df["denominazione_regione"],
        hovertemplate=(
            "<b>%{text}</b><br><br>" + value + "=%{z}<br>"
            "totale positivi=%{customdata[1]}<br>"
            "dimessi guariti=%{customdata[2]}<br>"
            "deceduti=%{customdata[3]}<br><br>"
            "<b>Totale per provincie</b><br>"
            "%{customdata[0]}"
            "<extra></extra>"
        ),
        customdata=region_day_df[
            ["tot_by_prov", "totale_positivi", "dimessi_guariti", "deceduti",]
        ],
    )

    fig = go.Figure(
        data=cp,
        layout=go.Layout(
            geo=GEO_LAYOUT,
            title=go.layout.Title(
                text=f"Distribuzione {value.replace('_', ' ')} {data:%Y-%m-%d}"
            ),
            height=HEIGHT,
        ),
    )
    return fig


def generate_map_province(value: str, data: DataType = None) -> go.Figure:
    """Generate the map region for the given data showing the given value
    
    Arguments:
        value {str} -- Value to visualize
    
    Keyword Arguments:
        data {Optional[dt.date]} -- Date to visualize (default: {None})
    
    Returns:
        go.Figure -- [description]
    """
    data = parse_data(data)
    df = get_province_data(value, data)
    log.debug(f"Generating map plot for {data}..")
    cp = go.Choropleth(
        geojson=map_data_province,
        z=df[value],
        locations=df["codice_provincia"],
        featureidkey="properties.prov_istat_code_num",
        colorscale=COLORSCALE,
        text=df["denominazione_provincia"],
        hovertemplate=(
            "<b>%{text} (%{customdata[0]})</b><br>"
            "Regione: %{customdata[1]}"
            "<br>" + value + "=%{z}<br>"
            "<extra></extra>"
        ),
        customdata=df[["sigla_provincia", "denominazione_regione",]],
    )

    fig = go.Figure(
        data=cp,
        layout=go.Layout(
            geo=GEO_LAYOUT,
            title=go.layout.Title(
                text=f"Distribuzione {value.replace('_', ' ')} {data:%Y-%m-%d}"
            ),
            height=HEIGHT,
        ),
    )
    return fig


def get_province_data(
    value: str, data: DataType, session: Optional[Session] = None
) -> pd.DataFrame:
    """Query data for province

    Arguments:
        value {str} -- Value selected
        data {Optional[Union[dt.datetime, str]]} -- Date

    Returns:
        pd.DataFrame -- Result dataframe
    """
    session = session or db.db.session
    max_data = session.query(func.max(db.ItalyRegionCase.data)).first()[0]
    data = (
        min(dt.datetime.strptime(data, "%Y-%m-%d").date(), max_data)
        if isinstance(data, str)
        else max_data
    )

    query = (
        session.query(
            db.ItalyProvince.codice_provincia,
            db.ItalyProvince.denominazione_provincia,
            # concat.label("provincia"),
            db.ItalyProvince.sigla_provincia,
            db.ItalyRegion.denominazione_regione,
            db.ItalyProvinceCase.__table__.c[value],
            db.ItalyProvinceCase.note_it,
            db.ItalyProvinceCase.note_en,
        )
        .filter(
            db.ItalyProvince.codice_provincia == db.ItalyProvinceCase.codice_provincia
        )
        .filter(db.ItalyProvince.codice_regione == db.ItalyRegion.codice_regione)
        .filter(db.ItalyProvinceCase.data == data)
    )
    return pd.DataFrame(query)


def get_region_data(
    value: str, data: dt.datetime, session: Optional[Session] = None
) -> pd.DataFrame:
    value = "deceduti" if value == "variazione_deceduti" else value
    session = session or db.db.session

    sub_query = (
        session.query(
            db.ItalyProvince.codice_regione,
            (
                func.string_agg(concat, "<br>").label("tot_by_prov")
                if session.bind.dialect.name == "postgresql"
                else func.GROUP_CONCAT(concat, "<br>").label("tot_by_prov")
            ),
        )
        .filter(
            db.ItalyProvince.codice_provincia == db.ItalyProvinceCase.codice_provincia
        )
        .filter(db.ItalyProvinceCase.data == data)
        .filter(db.ItalyProvince.codice_provincia < 200)
        .group_by(db.ItalyProvince.codice_regione)
    ).subquery()

    columns = ["totale_positivi", "dimessi_guariti", "deceduti"]

    select_columns = set(columns + [value])

    query = (
        session.query(
            db.ItalyRegion.codice_regione,
            db.ItalyRegion.denominazione_regione,
            *[db.ItalyRegionCase.__table__.columns[col] for col in select_columns],
            sub_query.c.tot_by_prov,
        )
        .filter(db.ItalyRegion.codice_regione == sub_query.c.codice_regione)
        .filter(db.ItalyRegionCase.data == data)
        .filter(db.ItalyRegionCase.codice_regione == db.ItalyRegion.codice_regione)
    )
    return pd.DataFrame(query)


def parse_data(data: Optional[str], session=None) -> dt.datetime:
    """Parse the data in string format

    Arguments:
        data {Optional[str]} -- Data

    Keyword Arguments:
        session {[type]} -- DB session (default: {None})

    Returns:
        dt.datetime -- Parsed data
    """
    session = session or db.db.session
    max_data = session.query(func.max(db.ItalyRegionCase.data)).first()[0]
    # max_data = region_df.data.dt.date.max()
    return (
        min(dt.datetime.strptime(data, "%Y-%m-%d").date(), max_data)
        if isinstance(data, str)
        else max_data
    )
