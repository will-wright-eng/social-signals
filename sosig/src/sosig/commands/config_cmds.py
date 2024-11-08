import typer

from ..core.config import PathManager, settings
from ..core.logger import log
from ..utils.display_service import display

config_cmds = typer.Typer()


@config_cmds.command()
def show(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Show current configuration"""
    if debug:
        log.set_debug(debug)

    paths = {
        "Config directory": PathManager.get_config_dir(),
        "Data directory": PathManager.get_data_dir(),
        "Database file": PathManager.get_data_dir() / settings.database.filename,
    }
    display.show_config(settings.model_dump(), paths)
