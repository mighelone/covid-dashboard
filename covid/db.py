from typing import Optional
import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
import pandas as pd
import logging
from urllib.request import urlopen
from urllib.error import HTTPError
from dateutil.parser import parse, ParserError
from .data import get_singlefile

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


conn = "mysql://root:example@127.0.0.1:3306/covid"

engine = create_engine(conn)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class ItalyRegion(Base):
    __tablename__ = "italy_region"
    data = Column(Date, primary_key=True)
    stato = Column(String(50))
    codice_regione = Column(Integer, primary_key=True)
    denominazione_regione = Column(String(50))
    lat = Column(String(50))
    long = Column(String(50))
    ricoverati_con_sintomi = Column(Integer)
    terapia_intensiva = Column(Integer)
    totale_ospedalizzati = Column(Integer)
    isolamento_domiciliare = Column(Integer)
    totale_positivi = Column(Integer)
    variazione_totale_positivi = Column(Integer)
    nuovi_positivi = Column(Integer)
    dimessi_guariti = Column(Integer)
    deceduti = Column(Integer)
    totale_casi = Column(Integer)
    tamponi = Column(Integer)
    note_it = Column(String(100), nullable=True)
    note_en = Column(String(100), nullable=True)


Base.metadata.create_all(engine)

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


def get_singlefile(date: dt.datetime):
    fname = f"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-{date:%Y%m%d}.csv"
    with urlopen(fname) as response:
        columns = next(response).decode().strip().split(",")
        trentino = []
        for line in response:
            values = [get_field(value) for value in line.decode().strip().split(",")]
            d = dict(zip(columns, values))
            if d['denominazione_regione'] in  ('P.A. Bolzano', 'P.A. Trento'):
                trentino.append(d)
            else:
                yield d
        trentino_all = {
            key: (value + trentino[1][key] if isinstance(value, int) else value)
            for key, value in trentino[0].items()
        }
        yield trentino_all



def insert_data(date: dt.datetime):
    # df = get_singlefile(date)
    # data = df.to_dict(orient='records')  
    session = Session()
    try:
        for row in get_singlefile(date):
            log.debug(f"Row -> {row}")
            row = ItalyRegion(**row)
            session.merge(row)
            # session.commit()
    except:
        log.exception("Rollback BS session")
        session.rollback()
    else:
        log.info("Commit DB session")
        session.commit()
    finally:
        log.info("Close DB session")
        session.close()


def update_db(date:Optional[dt.datetime]=None, from_begin=False):
    
    date = date or dt.datetime.now()
    start_date = dt.datetime(2020, 2, 24) if from_begin else date

    for day in pd.date_range(start=start_date, end=date, freq="D"):
        log.info(f"Reading data for {day}")
        try:
            insert_data(date=day)
        except HTTPError:
            log.error(f"No data for {day}")





