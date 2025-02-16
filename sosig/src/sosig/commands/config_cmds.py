import typer

from ..core.db import get_db
from ..core.config import PathManager, settings
from ..core.logger import log
from ..utils.gh_utils import GitCommandError, DefaultCommandRunner
from ..utils.display_service import display

config_cmds = typer.Typer()


@config_cmds.command()
def show(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    db_path_only: bool = typer.Option(False, "--db-path", help="Show only database path"),
):
    """Show current configuration"""
    if debug:
        log.set_debug(debug)

    if db_path_only:
        print(str(PathManager.get_data_dir() / settings.database.filename))
        return

    paths = {
        "Config directory": str(PathManager.get_config_dir()),
        "Data directory": str(PathManager.get_data_dir()),
        "Database file": str(PathManager.get_data_dir() / settings.database.filename),
    }
    display.show_config(settings, paths)


@config_cmds.command()
def init(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Initialize application and verify dependencies"""
    if debug:
        log.set_debug(debug)

    runner = DefaultCommandRunner()
    required_tools = {
        "git": ["git", "--version"],
        "gh": ["gh", "--version"],
        "wc": ["which", "wc"],
    }

    # Check required tools
    missing_tools = []
    for tool, command in required_tools.items():
        try:
            runner.run_command(command, ".")
            log.debug(f"✓ Found {tool}")
        except GitCommandError:
            missing_tools.append(tool)
            log.error(f"✗ Missing required tool: {tool}")

    if missing_tools:
        display.error(f"Missing required tools: {', '.join(missing_tools)}")
        raise typer.Exit(1)

    # Initialize database
    try:
        get_db()
        log.debug(f"✓ Initialized database at {PathManager.get_data_dir() / settings.database.filename}")
        display.success("Initialization complete!")
    except Exception as e:
        display.error(f"Failed to initialize database: {str(e)}")
        raise typer.Exit(1)
