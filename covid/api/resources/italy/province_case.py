import marshmallow
from flask.views import MethodView
from flask_smorest import Blueprint

from ....db import ItalyRegion, ItalyProvince, ItalyProvinceCase
from ....extension import db, ma


class ItalyProvinceCaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItalyProvinceCase

    denominazione_provincia = ma.auto_field(
        "denominazione_provincia", model=ItalyProvince
    )
    denominazione_regione = ma.auto_field("denominazione_regione", model=ItalyRegion)


class QueryArgsSchema(ma.SQLAlchemySchema):
    class Meta:
        # necessary for pagination parameters
        # https://flask-smorest.readthedocs.io/en/latest/arguments.html#multiple-arguments-schemas
        unknown = marshmallow.EXCLUDE

    start_data = ma.auto_field("data", model=ItalyProvinceCase, required=False)
    region = ma.auto_field("denominazione_regione", model=ItalyRegion, required=False)
    province = ma.auto_field(
        "denominazione_provincia", model=ItalyProvince, required=False
    )


def register_italy_province_case_api(bp: Blueprint):
    @bp.route("italy/province_cases")
    class ProvinceCaseView(MethodView):
        @bp.arguments(QueryArgsSchema, location="query")
        @bp.response(ItalyProvinceCaseSchema(many=True))
        @bp.paginate()
        def get(self, kwargs, pagination_parameters):
            query = (
                db.session.query(
                    *[col for col in ItalyProvinceCase.__table__.columns],
                    ItalyProvince.denominazione_provincia,
                    ItalyRegion.denominazione_regione,
                )
                .filter(
                    ItalyProvince.codice_provincia == ItalyProvinceCase.codice_provincia
                )
                .filter(ItalyProvince.codice_regione == ItalyRegion.codice_regione)
            )
            if "data" in kwargs:
                query = query.filter(ItalyProvinceCase.data >= kwargs["data"])
            if "denominazione_regione" in kwargs:
                query = query.filter(
                    ItalyRegion.denominazione_regione == kwargs["denominazione_regione"]
                )
            if "denominazione_provincia" in kwargs:
                query = query.filter(
                    ItalyProvince.denominazione_provincia
                    == kwargs["denominazione_provincia"]
                )
            pagination_parameters.item_count = query.count()
            return query.offset(pagination_parameters.first_item).limit(
                pagination_parameters.last_item - pagination_parameters.first_item
            )
