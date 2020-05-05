import datetime as dt
import logging
import os
import urllib

#%%
from pathlib import Path

import numpy as np
import pandas as pd
import sqlalchemy as sql

# %%
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from covid import db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# %%


def cast_int(x):
    try:
        res = int(x)
    except ValueError:
        res = None
    finally:
        return res


def cast_float(x):
    try:
        res = float(x)
    except ValueError:
        res = None
    finally:
        return res


schema = {
    "ID": int,
    "Updated": lambda x: dt.datetime.strptime(x, "%m/%d/%Y"),
    "Confirmed": cast_int,
    "ConfirmedChange": cast_int,
    "Deaths": cast_int,
    "DeathsChange": cast_int,
    "Recovered": cast_int,
    "RecoveredChange": cast_int,
    "Latitude": cast_float,
    "Longitude": cast_float,
    "ISO2": str,
    "ISO3": str,
    "Country_Region": str,
    "AdminRegion1": str,
    "AdminRegion2": str,
}

map_columns = {
    "ID": "id",
    "Updated": "updated",
    "Confirmed": "confirmed",
    "ConfirmedChange": "confirmed_change",
    "Deaths": "deaths",
    "DeathsChange": "deaths_change",
    "Recovered": "recovered",
    "RecoveredChange": "recovered_change",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "ISO2": "iso2",
    "ISO3": "iso3",
    "Country_Region": "country_region",
    "AdminRegion1": "admin_region_1",
    "AdminRegion2": "admin_region_2",
}


#%%
if __name__ == "__main__":
    conn = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://covid:FabrizioCorona@localhost:5432/covid",
    )
    session = db.get_db_session(conn)
    count = session.query(db.WorldCase).count()
    log.info(f"Rows before update={count}")
    url = "https://raw.githubusercontent.com/microsoft/Bing-COVID-19-Data/master/data/Bing-COVID19-Data.csv"

    with urllib.request.urlopen(url) as f:
        header = next(f).decode().strip().split(",")
        if set(header) != set(schema):
            log.warning(f"Header={header} different from schema={schema}")
        log.info(header)
        for line in f:

            try:
                d = {
                    map_columns[key]: schema[key](value)
                    for key, value in zip(header, line.decode().strip().split(","))
                }
            except:
                log.info(f"Can't read {line.decode()}")
            else:
                session.merge(db.WorldCase(**d))

    session.commit()
    count = session.query(db.WorldCase).count()
    log.info(f"Rows after update={count}")
    session.close()
    #%%
    # res = (
    #     session.query(
    #         WordCase.admin_region_1,
    #         WordCase.admin_region_2,
    #         WordCase.confirmed_change,
    #         WordCase.deaths_change,
    #     )
    #     .filter(WordCase.country_region == "Italy")
    #     .filter(WordCase.updated == dt.date(2020, 4, 23))
    #     .all()
    # )

    # # %%
    # res = (
    #     session.query(
    #         WordCase.updated,
    #         WordCase.admin_region_1,
    #         WordCase.admin_region_2,
    #         WordCase.confirmed_change,
    #         WordCase.deaths_change,
    #     )
    #     .filter(WordCase.country_region == "Italy")
    #     .filter(WordCase.admin_region_1 == "")
    #     .order_by(WordCase.updated)
    #     .all()
    # )

# %%
