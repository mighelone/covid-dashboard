import datetime as dt
import logging

import click

from covid import db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@click.group()
@click.pass_context
def italy(ctx: click.Context):
    """Manage the COVID 19 database for Italy
    """


@italy.command()
@click.option(
    "--full/--no-full", default=False, help="Fully populate database from starting date"
)
@click.option(
    "--start_date",
    default=dt.datetime.today().strftime("%Y-%m-%d"),
    type=click.DateTime(),
    help="Starting date for retriving new data to update db",
)
@click.option(
    "--end_date",
    default=dt.datetime.today().strftime("%Y-%m-%d"),
    type=click.DateTime(),
    help="Last day to update db",
)
@click.pass_context
def update(
    ctx: click.Context, full: bool, start_date: dt.datetime, end_date: dt.datetime
):
    """
    Update the province/region case tables with new data
    """
    session = db.get_db_session(ctx.obj["db_conn"])
    log.info(f"Updating tables casi...")
    db.update_db(
        start_date=start_date, end_date=end_date, from_begin=full, session=session
    )
    session.close()


@italy.command()
@click.pass_context
def init(ctx: click.Context):
    """
    Init the province/region tables with basic data. 
    Run update after to populate the province/region case tables
    """
    session = db.get_db_session(ctx.obj["db_conn"])
    # session = db.Session(bind=sqlalchemy.create_engine(db_conn))
    log.info(f"Initializing table italy_regione...")
    db.create_table_region(session=session)
    log.info(f"Initializing table italy_province...")
    db.create_table_province(session=session)
    session.close()
