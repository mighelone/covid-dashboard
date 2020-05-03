from flask import Flask
from flask_smorest import Api, Blueprint, abort
from .resources.italy.region import register_italy_regions_api


def register_api(app: Flask) -> Api:
    """Register the smorest Api on the Flask app

    Arguments:
        app {Flask} -- Flask app

    Returns:
        Api -- Registered Api
    """
    api = Api(app)
    api_bp = Blueprint("api", "api", url_prefix="/api", description="Covid-19 Rest API")
    register_italy_regions_api(api_bp)

    api.register_blueprint(api_bp)
    return api
