from ....extension import ma, db
from ....db import ItalyRegion


class ItalyRegionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItalyRegion
        load_instance = True  # convert json to a Pet object
