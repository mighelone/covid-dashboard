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
        def get(self, kwargs):
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

            return query
