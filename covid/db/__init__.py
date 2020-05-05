import os
import logging
import datetime as dt
from typing import Any, Dict, List, Iterator, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd
from sqlalchemy import (
    Date,
    Float,
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from dateutil.parser import ParserError, parse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

from ..extension import db
from .world_case import WorldCase
from .italy_region import ItalyRegion
from .italy_province import ItalyProvince
from .italy_region_case import ItalyRegionCase
from .italy_province_case import ItalyProvinceCase

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

Base = db.Model


def get_db_session(conn: Optional[str] = None):
    conn = conn or os.environ.get(
        "DB_CONN", "mysql://root:superset@127.0.0.1:3306/covid"
    )
    engine = create_engine(conn)
    log.info(f"Connected to {engine}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_field(field: str):
    try:
        result = int(field)
    except ValueError:
        try:
            result = float(field)
        except ValueError:
            try:
                result = parse(field).date()
            except ParserError:
                result = field
    return result


def get_singlefile(uri: str) -> Iterator[Dict[str, Any]]:
    # assert area in ('regioni', 'province'), "area should be defined as regioni/province"
    # fname = f"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-{area}-{date:%Y%m%d}.csv"
    with urlopen(uri) as response:
        columns = next(response).decode().strip().split(",")
        for line in response:
            try:
                values = [
                    get_field(value)
                    for value in line.decode("latin-1").strip().split(",")
                ]
            except:
                log.error(f"Error in {line}")
            else:
                yield dict(zip(columns, values))


def get_singlefile_regioni(
    date: Optional[dt.datetime] = None,
) -> Iterator[Dict[str, Any]]:

    date = date.strftime("%Y%m%d") if date else "latest"

    uri = f"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-{date}.csv"
    # https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv
    trentino = []
    for row in get_singlefile(uri):
        if row["denominazione_regione"] in ("P.A. Bolzano", "P.A. Trento"):
            trentino.append(row)
        else:
            yield row
    trentino_all = {
        key: (value + trentino[1][key] if (isinstance(value, int)) else value)
        for key, value in trentino[0].items()
    }
    trentino_all["codice_regione"] = 4
    trentino_all["denominazione_regione"] = "Trentino Alto Adige"
    yield trentino_all


def get_singlefile_province(
    date: Optional[dt.datetime] = None,
) -> Iterator[Dict[str, Any]]:
    date = date.strftime("%Y%m%d") if date else "latest"
    uri = f"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-{date}.csv"
    yield from get_singlefile(uri)


def insert_data(
    date: dt.datetime, Table: Base, get_file, session: Optional[Session] = None
):
    # df = get_singlefile(date)
    # data = df.to_dict(orient='records')
    close_session = session is None
    session = session or get_db_session()
    columns = [column.key for column in Table.__table__.columns]
    # province_columns = [column.key for column in ItalyProvinceCase.__table__.columns]
    try:
        log.debug(f"Adding data for {Table.__tablename__} on {date:%Y-%m-%d}...")
        for row in get_file(date):
            log.debug(f"Row -> {row}")
            row = Table(**{col: row[col] for col in columns})
            session.merge(row)
    except:
        # log.exception("Rollback BS session")
        session.rollback()
        raise
    else:
        log.debug("Commit DB session")
        session.commit()
    finally:
        log.debug("Close DB session")
        if close_session:
            session.close()


def create_table_region(session: Optional[Session] = None):
    """Initialize the italy_region table
    
    Arguments:
        session {Optional[Session]} -- DB session if none a new one is created and closed 
    """
    columns = [column.key for column in ItalyRegion.__table__.columns]
    close_session = session is None
    session = session or get_db_session()
    try:
        for row in get_singlefile_regioni():
            session.merge(ItalyRegion(**{col: row[col] for col in columns}))
    except:
        session.rollback()
        raise
    else:
        session.commit()
    finally:
        if close_session:
            session.close()


def create_table_province(session: Optional[Session] = None):
    """Initialize the italy_region table
    
    Arguments:
        session {Optional[Session]} -- DB session if none a new one is created and closed 
    """
    columns = [column.key for column in ItalyProvince.__table__.columns]
    close_session = session is None
    session = session or get_db_session()
    try:
        for row in get_singlefile_province():
            session.merge(ItalyProvince(**{col: row[col] for col in columns}))
    except:
        session.rollback()
        raise
    else:
        session.commit()
    finally:
        if close_session:
            session.close()


def update_db(session: Session, date: Optional[dt.datetime] = None, from_begin=False):

    date = date or dt.datetime.now()
    start_date = dt.datetime(2020, 2, 24) if from_begin else date
    for day in pd.date_range(start=start_date, end=date, freq="D"):
        log.info(f"Reading data for {day}")
        try:
            log.info("... reading regioni ...")
            insert_data(
                date=day,
                Table=ItalyRegionCase,
                get_file=get_singlefile_regioni,
                session=session,
            )
        except HTTPError:
            log.error(f"No data for {day}")
        try:
            log.info("... reading province ...")
            insert_data(
                date=day,
                Table=ItalyProvinceCase,
                get_file=get_singlefile_province,
                session=session,
            )
        except HTTPError:
            log.error(f"No data for {day}")
