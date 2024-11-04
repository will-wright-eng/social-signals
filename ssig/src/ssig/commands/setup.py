import json

import typer
from rich.console import Console

from ..utils.setup_utils import ConfigManager

setup_cmds = typer.Typer()
console = Console()


@setup_cmds.command()
def config_show():
    """Show current configuration"""
    config_manager = ConfigManager()
    console.print_json(json.dumps(config_manager.get_config().model_dump(), indent=2))


@setup_cmds.command()
def config_set(
    key: str = typer.Argument(..., help="Configuration key (dot notation, e.g., 'metrics.weights.age')"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set a configuration value"""
    config_manager = ConfigManager()

    # Parse the key path
    keys = key.split(".")
    updates = {}
    current = updates

    # Build nested dictionary
    for k in keys[:-1]:
        current[k] = {}
        current = current[k]

    # Set the value, converting to appropriate type
    try:
        # Try to convert to number if possible
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


if __name__ == "__main__":
    # Example usage
    config_manager = ConfigManager()
    config = config_manager.get_config()
    print(f"Loaded config from: {config_manager.config_file}")
    print(json.dumps(config.model_dump(), indent=2))
