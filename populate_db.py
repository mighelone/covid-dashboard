import click
import datetime as dt
import logging
import sqlalchemy

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from covid import db


@click.command()
@click.option(
    "--db-conn",
    "-d",
    default="sqlite:///covid.db",
    envvar="DB_CONN",
    help="Database connection",
)
@click.option("--full/--no-full", default=False, help="Fully populate database")
@click.option(
    "--date", default=dt.datetime.today().strftime("%Y-%m-%d"), type=click.DateTime()
)
def main(db_conn: str, full: bool, date: dt.datetime):
    session = db.get_db_session(db_conn)
    # session = db.Session(bind=sqlalchemy.create_engine(db_conn))
    log.info(f"Initializing table italy_regione...")
    db.create_table_region(session=session)
    log.info(f"Initializing table italy_province...")
    db.create_table_province(session=session)
    log.info(f"Updating tables casi...")
    db.update_db(date=date, from_begin=full, session=session)


if __name__ == "__main__":
    main()
