from flask.views import MethodView
from flask_smorest import Blueprint

from ....db import ItalyRegion
from ....extension import ma


class ItalyRegionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItalyRegion
        load_instance = True


def register_italy_regions_api(bp: Blueprint):
    """Register the API for italy region

    Arguments:
        bp {Blueprint} -- Smorest Blueprint
    """

    @bp.route("italy/regions")
    class RegionView(MethodView):
        # @bpb.arguments(ItalyRegionSchema, location="query")
        @bp.response(
            schema=ItalyRegionSchema(many=True),
            description="List of Italian regions",
            example={
                "codice_regione": 20,
                "denominazione_regione": "Sardegna",
                "lat": 39.2153,
                "long": 9.11062,
            },
        )
        def get(self):
            """Get the list of Italian regions

            Return a list of Italian regions
            """
            return ItalyRegion.query
