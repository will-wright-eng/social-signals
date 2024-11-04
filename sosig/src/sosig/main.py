import typer

from .commands.setup import setup_cmds
from .commands.gh_metrics import gh_cmds

app = typer.Typer(add_completion=False)

app.add_typer(setup_cmds, name="config", help="config operations")
app.add_typer(gh_cmds, name="gh", help="ghmetrics operations")


def entry_point():
    app()


if __name__ == "__main__":
    entry_point()
