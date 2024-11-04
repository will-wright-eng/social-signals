import json

import typer
from rich.console import Console

from ..core.config import settings, get_data_dir, get_config_dir
from ..utils.setup_utils import ConfigManager

setup_cmds = typer.Typer()
console = Console()


@setup_cmds.callback()
def callback():
    """Setup and configuration commands."""
    pass


@setup_cmds.command()
def show():
    """Show current configuration"""
    config_manager = ConfigManager()
    console.print_json(json.dumps(config_manager.get_config().model_dump(), indent=2))
    config_dir = get_config_dir()
    data_dir = get_data_dir()
    console.print("[bold]Application Paths:[/bold]")
    console.print(f"Config directory: {config_dir}")
    console.print(f"Data directory: {data_dir}")
    console.print(f"Database file: {data_dir / settings.database.filename}")
    console.print(f"Config file: {config_dir / 'config.json'}")


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
        console.print(f"[green]Updated {key} to {value}[/green]")

    except Exception as e:
        console.print(f"[red]Error updating config: {str(e)}[/red]")
