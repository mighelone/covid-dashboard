from flask_smorest import Api, Blueprint, abort

api_bp = Blueprint("api", "api", url_prefix="/api", description="Covid-19 Rest API")
