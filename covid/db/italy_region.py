from ..extension import db


class ItalyRegion(db.Model):
    __tablename__ = "italy_region"
    codice_regione = db.Column(db.Integer, primary_key=True)
    denominazione_regione = db.Column(db.String(50))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)

    def __repr__(self):
        return f"<{self.codice_regione}:{self.denominazione_regione}>"
