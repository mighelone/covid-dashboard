from typing import Union
import click
import orjson
import numpy as np
import logging
from simplification.cutil import simplify_coords
import geojson


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# with open("data/limits_IT_regions.geojson") as f:
#     data = orjson.loads(f.read())

# factor = 8


def reduce_polygon(
    geometry: geojson.geometry.Polygon, epsilon: float = 0.01
) -> geojson.geometry.Polygon:
    """Reduce and existing polygon using RDP algorithj
    
    Arguments:
        geometry {geojson.geometry.Polygon} -- Original polygon 
    
    Keyword Arguments:
        epsilon {float} -- Epsilon of the coeffiecient (smaller is more accurate with more points) (default: {0.01})
    
    Returns:
        geojson.geometry.Polygon -- Reduced geometry
    """
    points = geometry["coordinates"]
    # n = len(points)
    points = [max(points, key=lambda x: len(x))]
    reduced_points = [simplify_coords(p, epsilon) for p in points]
    # geometry["coordinates"] = reduced_points
    return geojson.Polygon(coordinates=reduced_points, validate=True)


def reduce_multipolygon(
    geometry: geojson.geometry.Polygon, epsilon: float = 0.01, limit: int = 100
) -> Union[geojson.geometry.MultiPolygon, geojson.geometry.Polygon]:
    """Reduce an exisiting MultiPolygon using RDP algorithm
    
    Arguments:
        geometry {geojson.geometry.Polygon} -- Original geometry
    
    Keyword Arguments:
        epsilon {float} -- Epsilon coefficient (default: {0.01})
        limit {int} -- Limit of point for skipping a polygon (default: {100})
    
    Returns:
        Union[geojson.geometry.MultiPolygon, geojson.geometry.Polygon] -- Reduced geometry, it can be reduced to a polygon if only one polygon is kept
    """
    polygons = geometry["coordinates"]
    polygons = [
        [simplify_coords(points, epsilon) for points in polygon if len(points) >= 100]
        for polygon in polygons
    ]
    polygons = [polygon for polygon in polygons if polygon]
    if len(polygons) > 1:
        return geojson.geometry.MultiPolygon(
            coordinates=polygons, validate=True, precision=6
        )
    else:
        return geojson.geometry.Polygon(coordinates=polygons[0], validate=True)


@click.command()
@click.argument("input_json", type=click.File(mode="r"))
@click.argument("output_json", type=click.File(mode="w"))
@click.option(
    "--epsilon",
    "-e",
    type=click.FLOAT,
    default=0.005,
    help="Epsilon coeffieent of Ramer–Douglas–Peucker algorithm for reducing the number of points",
)
@click.option(
    "--limit",
    "-l",
    type=click.INT,
    default=100,
    help="Mininum number of points for keeping a polygon",
)
def main(input_json, output_json, epsilon: float, limit: int):

    data = geojson.load(input_json)

    for region in data["features"]:
        geo = region["geometry"]
        if geo["type"] == "Polygon":
            new_geo = reduce_polygon(geo, epsilon)
        elif geo["type"] == "MultiPolygon":
            new_geo = reduce_multipolygon(geo, epsilon)
        else:
            raise ValueError(f"{geo['type']}")
        region["geometry"] = new_geo

    geojson.dump(data, output_json)


if __name__ == "__main__":
    main()
