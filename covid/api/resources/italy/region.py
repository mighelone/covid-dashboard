from flask.views import MethodView
from flask_smorest import Blueprint

from ....extension import ma, db
from ....db import ItalyRegion

# from ... import api_bp


class ItalyRegionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItalyRegion
        load_instance = True  # convert json to a Pet object


def register_italy_regions_api(bp: Blueprint):
    """Register the API for italy region

    Arguments:
        bp {Blueprint} -- Smorest Blueprint
    """

    @bp.route("italy/regions")
    class RegionView(MethodView):
        # @bpb.arguments(ItalyRegionSchema, location="query")
        @bp.response(
            schema=ItalyRegionSchema(many=True), description="List of Italian regions"
        )
        def get(self):
            """Get the list of Italian regions

            Return a list of Italian regions
            """
            return ItalyRegion.query
