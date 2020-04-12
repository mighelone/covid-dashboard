from typing import Dict, Any
import pandas as pd
import json
import os

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
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../data/limits_IT_regions.geojson'))

    with open(path, "r") as f:
        data = json.load(f)
    return data
