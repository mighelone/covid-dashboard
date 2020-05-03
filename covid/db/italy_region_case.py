from ..extension import db


class ItalyRegionCase(db.Model):
    __tablename__ = "italy_region_case"
    data = db.Column(db.Date, primary_key=True)
    codice_regione = db.Column(
        db.Integer, db.ForeignKey("italy_region.codice_regione"), primary_key=True
    )
    ricoverati_con_sintomi = db.Column(db.Integer)
    terapia_intensiva = db.Column(db.Integer)
    totale_ospedalizzati = db.Column(db.Integer)
    isolamento_domiciliare = db.Column(db.Integer)
    totale_positivi = db.Column(db.Integer)
    variazione_totale_positivi = db.Column(db.Integer)
    nuovi_positivi = db.Column(db.Integer)
    dimessi_guariti = db.Column(db.Integer)
    deceduti = db.Column(db.Integer)
    totale_casi = db.Column(db.Integer)
    tamponi = db.Column(db.Integer)
    note_it = db.Column(db.String(100), nullable=True)
    note_en = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<{self.data}:{self.codice_regione}>"
