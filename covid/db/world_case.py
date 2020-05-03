from ..extension import db


class WorldCase(db.Model):
    __tablename__ = "word_case"  # TODO rename table

    date = db.Column(db.Date, primary_key=True)
    country = db.Column(db.String(100), primary_key=True)
    admin = db.Column(db.String(100), primary_key=True)
    province = db.Column(db.String(100), primary_key=True)
    updated = db.Column(db.DateTime)
    confirmed = db.Column(db.Integer)
    active = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    recovered = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
