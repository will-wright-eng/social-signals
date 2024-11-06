import typer

from ..core.config import settings, get_data_dir, get_config_dir
from ..utils.setup_utils import ConfigManager
from ..utils.display_service import display

setup_cmds = typer.Typer()


@setup_cmds.command()
def show():
    """Show current configuration"""
    config_manager = ConfigManager()
    paths = {
        "Config directory": get_config_dir(),
        "Data directory": get_data_dir(),
        "Database file": get_data_dir() / settings.database.filename,
        "Config file": get_config_dir() / "config.json",
    }
    display.show_config(config_manager.get_config().model_dump(), paths)


@setup_cmds.command()
def set(
    key: str = typer.Argument(..., help="Configuration key (dot notation, e.g., 'metrics.weights.age')"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set a configuration value"""
    config_manager = ConfigManager()

    keys = key.split(".")
    updates = {}
    current = updates

    for k in keys[:-1]:
        current[k] = {}
        current = current[k]

    try:
        if value.lower() == "true":
            current[keys[-1]] = True
        elif value.lower() == "false":
            current[keys[-1]] = False
        else:
            try:
                if "." in value:
                    current[keys[-1]] = float(value)
                else:
                    current[keys[-1]] = int(value)
            except ValueError:
                current[keys[-1]] = value

        config_manager.update_config(updates)
        display.success(f"Updated {key} to {value}")

    except Exception as e:
        display.error(f"Error updating config: {str(e)}")
