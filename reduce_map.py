import click
import orjson
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# with open("data/limits_IT_regions.geojson") as f:
#     data = orjson.loads(f.read())

# factor = 8


def reduce_list(l, factor):
    if len(l[0]) == 2:

        reduced = np.array(l)[::factor].tolist() if len(l) > 20 else l
    else:

        reduced = [reduce_list(li, factor) for li in l]

    return reduced


# f = data["features"][0]["geometry"]["coordinates"]


# new_features = []

# for feature in data["features"]:
#     feature["geometry"]["coordinates"] = reduce_list(feature["geometry"]["coordinates"])


# with open("italy-reduced.mapjson", "wb") as f:
#     f.write(orjson.dumps(data))


@click.command()
@click.argument("input_json", type=click.File(mode="r"))
@click.argument("output_json", type=click.File(mode="wb"))
@click.option(
    "--factor", "-f", type=click.INT, default=8, help="Number of points to filter"
)
def main(input_json, output_json, factor):
    data = orjson.loads(input_json.read())

    for feature in data["features"]:
        feature["geometry"]["coordinates"] = reduce_list(
            feature["geometry"]["coordinates"], factor
        )

    output_json.write(orjson.dumps(data))


if __name__ == "__main__":
    main()
