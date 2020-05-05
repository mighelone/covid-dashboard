from flask.views import MethodView
from flask_smorest import Blueprint

from ....db import ItalyRegion, ItalyProvince
from ....extension import db, ma


class ItalyProvinceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItalyProvince
        load_instance = True

    denominazione_regione = ma.auto_field("denominazione_regione", model=ItalyRegion)


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
            """Get the list of Italian provinces

            Return a list of Italian provinces. The provinces can be filtered by region
            """
            query = db.session.query(
                ItalyProvince.codice_provincia,
                ItalyProvince.codice_regione,
                ItalyProvince.denominazione_provincia,
                ItalyRegion.denominazione_regione,
                ItalyProvince.lat,
                ItalyProvince.long,
            )
            query = query.filter(ItalyProvince.codice_provincia < 200).filter(
                ItalyProvince.codice_regione == ItalyRegion.codice_regione
            )
            if kwargs:
                query = query.filter(
                    ItalyRegion.denominazione_regione == kwargs["denominazione_regione"]
                )
            return query
