import logging

import click

from .cli_italy import italy
from .cli_world import world

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@click.group()
@click.option(
    "--db-conn",
    "-d",
    default="sqlite:///covid.db",
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


# main.add_command(.)

main.add_command(italy)
main.add_command(world)
