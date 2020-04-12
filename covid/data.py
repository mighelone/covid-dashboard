from typing import Dict, Any
import pandas as pd
import json
import os
import datetime as dt
import numpy as np
import logging
from pathlib import Path

log = logging.getLogger(__name__)

# data_path = os.path.abspath(os.path.dirname(__file__))
data_path = Path(os.path.dirname(__file__)).absolute()

URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json"


def get_italy_regional_data(url=URL) -> pd.DataFrame:
    """Read the Italian regional data from COVID-19 github repo
    
    Keyword Arguments:
        url {str} -- Url of data (default: {"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json"})
    
    Returns:
        pd.DataFrame -- dataframe
    """
    covid = pd.read_json(url)
    covid = covid.drop(17)  # TODO sum trento+bolzano
    covid["codice_regione"] = covid["codice_regione"].apply(lambda x: f"{x:02}")
    return covid


def get_italy_map_region() -> Dict[str, Any]:
    """Read the geojson regional data for Italy
    
    Returns:
        [type] -- [description]
    """
    # path = os.path.join(data_path, )
    path = data_path / "../data/limits_IT_regions.geojson"

    with open(path, "r") as f:
        data = json.load(f)
    return data


def get_singlefile(date):
    f = f"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-{date:%Y%m%d}.csv"
    try:
        df = pd.read_csv(f)
    except:
        df = pd.DataFrame()
    else:
        return df

def get_time_data() -> pd.DataFrame:
    today = dt.date.today()
    fname: Path = data_path / "../data/historical_region.json"
    if fname.exists():
        log.info(f"{fname} already exists reading from local fs")
        df = pd.read_json(fname)
    else:
        log.info(f"{fname} not downloaded yet, reading from github")
        df: pd.DataFrame = (
            pd.concat(
                [
                    get_singlefile(day)
                    for day in pd.date_range(
                        start="2020-02-24", end=today, freq="D"
                    )
                ]
            )
            .astype({"data": np.datetime64})
            .sort_values(["codice_regione", "data"])
        )
        # import pdb; pdb.set_trace()
        df.to_json(fname, orient='records', date_format='iso')
    return df


