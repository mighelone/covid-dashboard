import orjson
import numpy as np

with open("data/limits_IT_regions.geojson") as f:
    data = orjson.loads(f.read())

factor = 8


def reduce_list(l):
    if len(l[0]) == 2:

        reduced = np.array(l)[::factor].tolist() if len(l) > 20 else l
    else:

        reduced = [reduce_list(li) for li in l]

    return reduced


# f = data["features"][0]["geometry"]["coordinates"]


new_features = []

for feature in data["features"]:
    feature["geometry"]["coordinates"] = reduce_list(feature["geometry"]["coordinates"])


with open("italy-reduced.mapjson", "wb") as f:
    f.write(orjson.dumps(data))
