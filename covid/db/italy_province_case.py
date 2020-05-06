from ..extension import db


class ItalyProvinceCase(db.Model):
    __tablename__ = "italy_province_case"
    data = db.Column(db.Date, primary_key=True)
    codice_provincia = db.Column(
        db.Integer, db.ForeignKey("italy_province.codice_provincia"), primary_key=True
    )
    totale_casi = db.Column(db.Integer)
    note_it = db.Column(db.String(100))
    note_en = db.Column(db.String(100))
