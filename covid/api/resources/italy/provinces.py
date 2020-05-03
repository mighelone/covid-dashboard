from flask.views import MethodView
from flask_smorest import Blueprint
import marshmallow as maw

from ....db import ItalyProvince, ItalyRegion
from ....extension import db, ma


class ItalyProvinceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItalyProvince
        load_instance = True


class RegionQueryArg(ma.SQLAlchemySchema):
    region = ma.auto_field("denominazione_regione", model=ItalyRegion, required=False)


def register_italy_provinces_api(bp: Blueprint):
    """Register the API for italy provinces

    Arguments:
        bp {Blueprint} -- Smorest Blueprint
    """

    @bp.route("italy/provinces")
    class ProvincesView(MethodView):
        @bp.arguments(RegionQueryArg, location="query")
        @bp.response(
            schema=ItalyProvinceSchema(many=True), description="List of Italian regions"
        )
        def get(self, kwargs):
            """Get the list of Italian regions

            Return a list of Italian regions
            """
            query = ItalyProvince.query
            if kwargs:
                query = query.filter(
                    ItalyProvince.codice_regione == ItalyRegion.codice_regione
                ).filter(
                    ItalyRegion.denominazione_regione == kwargs["denominazione_regione"]
                )
            return query
