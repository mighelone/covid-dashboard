from ..extension import db


class ItalyProvince(db.Model):
    __tablename__ = "italy_province"
    codice_provincia = db.Column(db.Integer, primary_key=True)
    sigla_provincia = db.Column(db.String(2))
    codice_regione = db.Column(db.Integer, db.ForeignKey("italy_region.codice_regione"))
    denominazione_provincia = db.Column(db.String(50))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)

    def __repr__(self):
        return f"<{self.codice_provincia}:{self.denominazione_provincia} ({self.codice_provincia})>"
