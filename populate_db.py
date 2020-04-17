import click
import datetime as dt
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from covid.db import update_db


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
    update_db(date=date, from_begin=full)


if __name__ == "__main__":
    main()
