import marshmallow
from flask.views import MethodView
from flask_smorest import Blueprint

from ....db import ItalyRegion, ItalyRegionCase
from ....extension import db, ma


class ItalyRegionCaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItalyRegionCase
        # load_instance = True

    denominazione_regione = ma.auto_field("denominazione_regione", model=ItalyRegion)


class QueryArgsSchema(ma.SQLAlchemySchema):
    class Meta:
        # necessary for pagination parameters
        # https://flask-smorest.readthedocs.io/en/latest/arguments.html#multiple-arguments-schemas # noqa: E501
        unknown = marshmallow.EXCLUDE

    start_data = ma.auto_field("data", model=ItalyRegionCase, required=False)
    # end_data = ma.auto_field("data", model=ItalyRegionCase, required=False)
    region = ma.auto_field("denominazione_regione", model=ItalyRegion, required=False)


def register_italy_region_case_api(bp: Blueprint):
    @bp.route("italy/region_cases")
    class RegionCaseView(MethodView):
        @bp.arguments(QueryArgsSchema, location="query")
        @bp.response(
            schema=ItalyRegionCaseSchema(many=True), description="Cases per region"
        )
        @bp.paginate()
        def get(self, kwargs, pagination_parameters):
            """Get the list of cases in Italy by region

            Return the list of cases in Italy by region. Data can be filtered by region
            and by a starting date.
            """
            query = db.session.query(
                *[col for col in ItalyRegionCase.__table__.columns],
                ItalyRegion.denominazione_regione,
            ).filter(ItalyRegionCase.codice_regione == ItalyRegion.codice_regione)
            if "data" in kwargs:
                query = query.filter(ItalyRegionCase.data >= kwargs["data"])
            if "denominazione_regione" in kwargs:
                query = query.filter(
                    ItalyRegion.denominazione_regione == kwargs["denominazione_regione"]
                )
            query.order_by(ItalyRegionCase.data, ItalyRegion.denominazione_regione)
            pagination_parameters.item_count = query.count()
            return query.offset(pagination_parameters.first_item).limit(
                pagination_parameters.last_item - pagination_parameters.first_item
            )
