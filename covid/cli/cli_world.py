import datetime as dt
import logging
import urllib

import click
import numpy as np
import pandas as pd
import sqlalchemy as sa
import sqlalchemy.sql.expression as expr
from sqlalchemy.ext.compiler import compiles

from covid import db

# conn = 'sqlite:///covid.db'
conn = "mysql://root:example@127.0.0.1:3306/covid"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Upsert(expr.Insert):
    pass


@compiles(Upsert, "mysql")
def compile_upsert(insert_stmt, compiler, **kwargs):
    """
    https://gist.github.com/timtadh/7811458
    """
    if insert_stmt._has_multi_parameters:
        keys = insert_stmt.parameters[0].keys()
    else:
        keys = insert_stmt.parameters.keys()
    pk = insert_stmt.table.primary_key
    auto = None
    if (
        len(pk.columns) == 1
        and isinstance(pk.columns.values()[0].type, sa.Integer)
        and pk.columns.values()[0].autoincrement
    ):
        auto = pk.columns.keys()[0]
        if auto in keys:
            keys.remove(auto)
    insert = compiler.visit_insert(insert_stmt, **kwargs)
    ondup = "ON DUPLICATE KEY UPDATE"
    updates = ", ".join(
        "%s = VALUES(%s)" % (c.name, c.name)
        for c in insert_stmt.table.columns
        if c.name in keys
    )
    if auto is not None:
        last_id = "%s = LAST_INSERT_ID(%s)" % (auto, auto)
        if updates:
            updates = ", ".join((last_id, updates))
        else:
            updates = last_id
    upsert = " ".join((insert, ondup, updates))
    return upsert


def read_data(path: str):

    df = pd.read_csv(path)  # , parse_dates=["Last_Update"])
    df = df.rename(
        columns={
            "Lat": "latitude",
            "Long_": "longitude",
            "Deaths": "deaths",
            "Confirmed": "confirmed",
            "active": "active",
            "Country_Region": "county",
            "Recovered": "recovered",
            "Last_Update": "updated",
            "Last Update": "updated",
            "Demised": "deaths",
            "Country/Region": "country",
            "Country_Region": "country",
            "Province/State": "province",
            "Province_State": "province",
            "Active": "active",
            "Admin2": "admin",
        }
    )

    df = df.astype({"updated": np.datetime64})
    columns = [
        # "FIPS",
        "admin",
        "province",
        "country",
        "updated",
        "latitude",
        "longitude",
        "confirmed",
        "deaths",
        "recovered",
        "active",
        # "Combined_Key",
    ]

    df = df.loc[:, columns]

    df["country"] = df["country"].replace(
        to_replace={
            "Korea, South": "South Korea",
            "Republic of Korea": "South Korea",
            "Mainland China": "China",
            "Hong Kong SAR": "Hong Kong",
            "Taipei and environs": "Taiwan",
            "Taiwan*": "Taiwan",
            "Macao SAR": "Macau",
            "Iran (Islamic Republic of)": "Iran",
            "Viet Nam": "Vietnam",
            "UK": "United Kingdom",
            " Azerbaijan": "Azerbaijan",
            "Bosnia and Herzegovina": "Bosnia",
            "Czech Republic": "Czechia",
            "Republic of Ireland": "Ireland",
            "North Ireland": "Ireland",
            "Republic of Moldova": "Moldova",
            "Russian Federation": "Russia",
            # African Countries
            "Congo (Brazzaville)": "Congo",
            "Congo (Kinshasa)": "Congo",
            "Republic of :e Congo": "Congo",
            "Gambia, The": "Gambia",
            "The Gambia": "Gam:a",
            # 'USA': 'America',
            "US": "USA",
            "Bahamas, The": "The Bahamas",
            "Bahamas": "The Baha:s",
            "st. Martin": "Saint Martin",
            "St. Martin": "Saint Martin",
            "Cruise Ship": "others",
        }
    )
    int_cols = ["confirmed", "deaths", "recovered", "active"]
    df = df.fillna({col: 0 for col in int_cols + ["latitude", "longitude"]}).astype(
        {col: np.int32 for col in int_cols}
    )

    df["province"] = df["province"].where(~df["province"].isnull(), df["country"])
    df["admin"] = df["admin"].where(~df["admin"].isnull(), df["country"])
    # df["updated"] = df["updated"].dt.date
    df = df.drop_duplicates(
        subset=["country", "updated", "admin", "province"], keep="last"
    )
    # df = df.fillna(value={'longitude': 0, 'latitude': 0})
    return df


BASE_PATH = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date:%m-%d-%Y}.csv"
START_DATE = dt.date(2020, 1, 22)


@click.group()
@click.pass_context
def world(ctx: click.Context):
    """Manage the COVID 19 database for World from CSSE"""


@world.command()
@click.option(
    "--full/--no-full", default=False, help="Fully populate database from starting date"
)
@click.option(
    "--date",
    default=dt.datetime.today().strftime("%Y-%m-%d"),
    type=click.DateTime(),
    help="Last day to update db",
)
@click.pass_context
def update(ctx: click.Context, full: bool, date: dt.datetime):
    """
    Update the world case table with new data
    """
    session = db.get_db_session(ctx.obj["db_conn"])
    date = date.date()
    start_date, n_days = (START_DATE, (date - START_DATE).days) if full else (date, 1)

    for i in range(0, n_days):
        date = start_date + dt.timedelta(days=i)
        log.info(f"Reading {date}")
        path = BASE_PATH.format(date=date)  # / f"{date:%m-%d-%Y}.csv"

        try:
            df = read_data(path)
        except urllib.error.HTTPError:
            log.error(f"No data found for {date} on {path}")
            continue
        else:
            df["date"] = date

        try:
            session.execute(Upsert(db.WorldCase, df.to_dict(orient="record")))
        except:
            log.error(f"Error inserting data on {date}")
            session.rollback()
        else:
            session.commit()

    session.close()
