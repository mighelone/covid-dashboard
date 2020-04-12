import pandas as pd
import json


def get_italy_regional_data(
    url="https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json",
) -> pd.DataFrame:
    covid = pd.read_json(url)
    covid = covid.drop(17)  # TODO sum trento+bolzano
    covid["codice_regione"] = covid["codice_regione"].apply(lambda x: f"{x:02}")
    return covid


def get_italy_map_region():
    with open(
        "/home/michele/Codes/python/dash-example/limits_IT_regions.geojson", "r"
    ) as f:
        data = json.load(f)
    return data
