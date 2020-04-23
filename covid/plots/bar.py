from typing import List, Optional
from sqlalchemy import func
import pandas as pd
import plotly.graph_objects as go
from .. import db

PLOT_OVERALL_COLUMNS = [
    "dimessi_guariti",
    "isolamento_domiciliare",
    "ricoverati_con_sintomi",
    "terapia_intensiva",
    "deceduti",
]


def generate_bar_plot_overall(
    region: str = "Italy", columns: List[str] = PLOT_OVERALL_COLUMNS,
):
    """Generate a stacked bar plot of the given columns for a region or for the whole country
    
    Keyword Arguments:
        region {str} -- Region to visualize (default: {"Italy"})
        columns {list} -- List of columns to plot as stacked bar (default: {["dimessi_guariti","isolamento_domiciliare","ricoverati_con_sintomi",
            "terapia_intensiva","deceduti",]})
    
    Returns:
        [type] -- figure
    """

    if region != "Italia":
        # df1 = df1.query("denominazione_regione==@region")
        query = (
            db.db.session.query(
                db.ItalyRegion.codice_regione,
                db.ItalyRegion.denominazione_regione,
                db.ItalyRegionCase.data,
                *[db.ItalyRegionCase.__table__.columns[col] for col in columns],
            )
            .filter(db.ItalyRegionCase.codice_regione == db.ItalyRegion.codice_regione)
            .filter(db.ItalyRegion.denominazione_regione == region)
        )
        df1 = pd.DataFrame(query)
    else:
        # df1 = df1.groupby(["data"], as_index=False).sum()
        query = db.db.session.query(
            db.ItalyRegionCase.data,
            *[
                func.sum(db.ItalyRegionCase.__table__.columns[col]).label(col)
                for col in columns
            ],
        ).group_by(db.ItalyRegionCase.data)
        df1 = pd.DataFrame(query)

    x = df1["data"]
    return go.Figure(
        data=[go.Bar(name=col.replace("_", " "), x=x, y=df1[col]) for col in columns],
        layout=go.Layout(
            plot_bgcolor="white",
            barmode="stack",
            legend=dict(
                x=0.02, y=0.98,  # title=f"<b> {region} </b>", traceorder="normal",
            ),
            title=f"{region}: andamento casi",
            height=400,
        ),
    )


def generate_bar_plot_provicie(provincia: str, value: str = "totale_casi"):
    query = (
        db.db.session.query(db.ItalyProvinceCase.data, db.ItalyProvinceCase.totale_casi)
        .filter(
            db.ItalyProvince.codice_provincia == db.ItalyProvinceCase.codice_provincia
        )
        .filter(db.ItalyProvince.denominazione_provincia == provincia)
    )
    df = pd.DataFrame(query)
    return go.Figure(
        data=[go.Bar(x=df["data"], y=df[value])],
        layout=go.Layout(
            plot_bgcolor="white",
            barmode="stack",
            legend=dict(
                x=0.02, y=0.98,  # title=f"<b> {region} </b>", traceorder="normal",
            ),
            title=f"{provincia}: {value.replace('_', ' ')}",
            height=400,
        ),
    )


def generate_bar_plot_selected(region="Italia", value: str = "totale_casi"):
    value_query, do_increment = (
        ("deceduti", True) if value == "variazione_deceduti" else (value, False)
    )

    if region == "Italia":
        query = (
            db.db.session.query(
                db.ItalyRegionCase.data,
                func.sum(db.ItalyRegionCase.__table__.columns[value_query]).label(
                    value_query
                ),
            )
            .filter(db.ItalyRegion.codice_regione == db.ItalyRegionCase.codice_regione)
            .group_by(db.ItalyRegionCase.data)
        )
    else:
        query = (
            db.db.session.query(
                db.ItalyRegionCase.data,
                db.ItalyRegionCase.__table__.columns[value_query],
            )
            .filter(db.ItalyRegion.codice_regione == db.ItalyRegionCase.codice_regione)
            .filter(db.ItalyRegion.denominazione_regione == region)
        )

    df1 = pd.DataFrame(query)

    if do_increment:
        # import pdb; pdb.set_trace()
        df1 = df1.assign(**{value: df1[value_query].diff()})

    return go.Figure(
        data=[
            go.Bar(
                name=value.replace("_", " "),
                x=df1["data"],
                y=df1[value],
                # line=go.scatter.Line(width=3)
            )
        ],
        layout=go.Layout(
            plot_bgcolor="white",
            barmode="stack",
            # yaxis=go.layout.YAxis(title=value.replace("_", " ")),
            legend=dict(
                x=0.02, y=0.98, title=f"<b> {region} </b>", traceorder="normal",
            ),
            title=f"{region}: {value.replace('_', ' ')}",
            height=400,
        ),
    )
