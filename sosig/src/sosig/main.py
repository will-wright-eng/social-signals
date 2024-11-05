import typer

from .commands.setup import setup_cmds
from .commands.db_cmds import db_cmds
from .commands.gh_metrics import gh_cmds

app = typer.Typer(add_completion=False)

app.add_typer(setup_cmds, name="config", help="config operations")
app.add_typer(gh_cmds, name="gh", help="ghmetrics operations")
app.add_typer(db_cmds, name="db", help="database operations")


def entry_point():
    app()


if __name__ == "__main__":
    entry_point()
