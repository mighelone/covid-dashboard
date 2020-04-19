import pytest
import datetime as dt
import os

os.environ["DB_CONN"] = "sqlite:///"
from covid import db


def test_get_singlefile():
    # TODO mock uri
    uri = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-20200401.csv"
    rows = list(db.get_singlefile(uri))

    assert len(rows) == 21


def test_get_singlefile_province():
    date = dt.datetime(2020, 4, 1)
    rows = list(db.get_singlefile_province(date))


@pytest.fixture
def session(scope="session") -> db.Session:
    sess = db.Session()
    sess.add(db.ItalyRegion(codice_regione=1, denominazione_regione="Sardegna"))
    sess.add(
        db.ItalyProvince(
            codice_provincia=1,
            sigla_provincia="CA",
            codice_regione=1,
            denominazione_provincia="Cagliari",
        )
    )
    sess.add(
        db.ItalyRegionCase(
            data=dt.date(2020, 4, 1), codice_regione=1, ricoverati_con_sintomi=50,
        )
    )
    sess.add(
        db.ItalyRegionCase(
            data=dt.date(2020, 4, 2), codice_regione=1, ricoverati_con_sintomi=52,
        )
    )
    sess.add(
        db.ItalyProvinceCase(
            data=dt.date(2020, 4, 1), codice_provincia=1, totale_casi=20,
        )
    )
    sess.add(
        db.ItalyProvinceCase(
            data=dt.date(2020, 4, 2), codice_provincia=1, totale_casi=21,
        )
    )
    sess.commit()
    yield sess

    sess.close()


def test_db_region(session):
    res = (
        session.query(
            db.ItalyRegionCase.data,
            db.ItalyRegion.codice_regione,
            db.ItalyRegion.denominazione_regione,
            db.ItalyRegionCase.ricoverati_con_sintomi,
        )
        # .join()
        .all()
    )
    assert len(res) == 2
    assert res == [
        (dt.date(2020, 4, 1), 1, "Sardegna", 50),
        (dt.date(2020, 4, 2), 1, "Sardegna", 52),
    ]


def test_db_region(session):
    res = (
        session.query(
            db.ItalyProvinceCase.data,
            db.ItalyProvince.codice_provincia,
            db.ItalyProvince.sigla_provincia,
            db.ItalyProvince.denominazione_provincia,
            db.ItalyRegion.denominazione_regione,
            db.ItalyProvinceCase.totale_casi,
        )
        # .join()
        .all()
    )
    assert res == [
        (dt.date(2020, 4, 1), 1, "CA", "Cagliari", "Sardegna", 20),
        (dt.date(2020, 4, 2), 1, "CA", "Cagliari", "Sardegna", 21),
    ]
