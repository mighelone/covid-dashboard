import os
import logging

import click
from dotenv import load_dotenv

from .cli_italy import italy
from .cli_world import world

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


load_dotenv(".env")
load_dotenv(".flaskenv")


@click.group()
@click.option(
    "--db-conn",
    "-d",
    default=os.environ.get("DATABASE_URL", "mysql://root:example@127.0.0.1:3306/covid"),
    envvar="DB_CONN",
    help="Database connection (sqlalchemy format)",
)
@click.pass_context
def main(ctx: click.Context, db_conn: str):
    """
    Manage the COVID 19 database
    """
    ctx.ensure_object(dict)
    ctx.obj["db_conn"] = db_conn


main.add_command(italy)
main.add_command(world)
