from typing import Dict, Any, List
import pandas as pd
import json
import os
import datetime as dt
import numpy as np
import logging
from pathlib import Path
from sqlalchemy import func

from . import db

log = logging.getLogger(__name__)

data_path = Path(os.path.dirname(__file__)).absolute()

URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json"


def get_db_region_data(conn: str) -> pd.DataFrame:
    """Get from the DB the pandas DF of the cases by region
    
    Arguments:
        conn {str} -- DB connection
    
    Returns:
        pd.DataFrame -- Resulting DF
    """
    log.info(f"Importing region data...")
    session = db.get_db_session(conn)
    try:
        query = session.query(
            *db.ItalyRegionCase.__table__.columns, db.ItalyRegion.denominazione_regione,
        ).filter(db.ItalyRegionCase.codice_regione == db.ItalyRegion.codice_regione)
        df = pd.DataFrame(query).astype({"data": np.datetime64})
    except:
        raise
    else:
        log.info(f"... data imported")
    finally:
        session.close()
    return df


def get_db_province_data(conn: str) -> pd.DataFrame:
    log.info(f"Importing province data...")
    session = db.get_db_session(conn)
    try:
        query = (
            session.query(
                *db.ItalyProvinceCase.__table__.columns,
                db.ItalyProvince.denominazione_provincia,
                db.ItalyProvince.sigla_provincia,
                db.ItalyProvince.codice_regione,
                db.ItalyRegion.denominazione_regione,
            )
            .filter(
                db.ItalyProvinceCase.codice_provincia
                == db.ItalyProvince.codice_provincia
            )
            .filter(db.ItalyProvince.codice_regione == db.ItalyRegion.codice_regione)
            .filter(
                #      db.ItalyProvince.sigla_provincia != ''
                db.ItalyProvinceCase.codice_provincia
                < 200
            )
        )
        df = pd.DataFrame(query).astype({"data": np.datetime64})
    except:
        raise
    else:
        log.info(f"... data imported")
    finally:
        session.close()
    return df


def get_italy_map(selection: str) -> Dict[str, Any]:
    """Read the geojson regional data for Italy
    
    Arguments:
        selection {str} -- Select regioni/province
    
    Returns:
        Dict[str, Any] -- Geojson
    """
    # path = data_path / "../data/limits_IT_regions.geojson"
    path = data_path / f"../data/italy-reduced-{selection}.geojson"

    with open(path, "r") as f:
        data = json.load(f)
    return data


def get_population_data() -> Dict[str, int]:
    with (data_path / "../data/world_population.json").open("r") as f:
        countries = {
            row["name"]: int(float(row["pop2020"]) * 1e3)
            for row in json.load(f)["data"]
        }

    countries["USA"] = countries.pop("United States")
    return countries
