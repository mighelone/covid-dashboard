from flask import Flask
from flask_smorest import Api, Blueprint

from .resources.italy import (
    register_italy_regions_api,
    register_italy_provinces_api,
    register_italy_region_case_api,
    register_italy_province_case_api,
)


def register_api(app: Flask) -> Api:
    """Register the smorest Api on the Flask app

    Arguments:
        app {Flask} -- Flask app

    Returns:
        Api -- Registered Api
    """
    api = Api(app)
    bp = Blueprint("api", "api", url_prefix="/api", description="Covid-19 Rest API")
    register_italy_regions_api(bp)
    register_italy_provinces_api(bp)
    register_italy_region_case_api(bp)
    register_italy_province_case_api(bp)

    api.register_blueprint(bp)
    return api
