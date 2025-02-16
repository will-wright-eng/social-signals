import os
import traceback
from typing import List

import typer

from .common import _init_services
from ..core.db import get_db
from ..core.logger import log
from ..utils.display_service import display

db_cmds = typer.Typer()


@db_cmds.command()
def stats(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Show database statistics."""
    if debug:
        log.set_debug(debug)
    try:
        db = get_db()
        stats = db.get_stats()
        display.show_db_stats(stats)
    except Exception as e:
        display.error(f"Error getting database statistics: {e}")
        raise typer.Exit(1)


@db_cmds.command()
def remove(
    drop_db: bool = typer.Option(False, "--drop-db", help="Drop the entire database file"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Remove a specific repository or drop the entire database."""
    if debug:
        log.set_debug(debug)
    try:
        db = get_db()

        if drop_db:
            if not typer.confirm("Are you sure you want to drop the entire database? This cannot be undone!"):
                raise typer.Abort()

            if db.remove_db(drop_db=True):
                display.success("Successfully dropped database file")
            return
        else:
            display.warn("Include --drop-db flag to drop the database file")
            raise typer.Exit(1)

    except Exception as e:
        display.error(f"Error dropping db: {e}")
        raise typer.Exit(1)


@db_cmds.command()
def vacuum(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Optimize the database by running VACUUM."""
    if debug:
        log.set_debug(debug)
    try:
        db = get_db()
        db.optimize()
        display.success("Successfully optimized database")
    except Exception as e:
        display.error(f"Error optimizing database: {e}")
        raise typer.Exit(1)


@db_cmds.command()
def schema(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Show database schema information."""
    if debug:
        log.set_debug(debug)
    try:
        db = get_db()
        schema_info = db.get_schema_info()

        # Display tables
        display.info("\nTables:")
        for table_name, table_info in schema_info["tables"].items():
            display.info(f"\n  {table_name}:")
            for column in table_info["columns"]:
                pk_marker = " (PK)" if column["primary_key"] else ""
                nullable = "" if column["nullable"] else " NOT NULL"
                display.info(f"    - {column['name']}: {column['type']}{nullable}{pk_marker}")

        # Display indexes
        if schema_info["indexes"]:
            display.info("\nIndexes:")
            for idx in schema_info["indexes"]:
                display.info(f"  - {idx['name']} (on {idx['table']})")

        # Display triggers
        if schema_info["triggers"]:
            display.info("\nTriggers:")
            for trigger in schema_info["triggers"]:
                display.info(f"  - {trigger['name']} (on {trigger['table']})")

    except Exception as e:
        display.error(f"Error getting schema information: {e}")
        raise typer.Exit(1)


@db_cmds.command()
def show(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Show all repository data from the database."""
    if debug:
        log.set_debug(debug)
    try:
        db = get_db()
        repositories = db.get_all_repositories()

        if not repositories:
            display.info("No repositories found in database")
            return

        # Use the new method that shows all fields
        display.show_full_repository_details(repositories)

    except Exception as e:
        display.error(f"Error dumping database contents: {e}")
        raise typer.Exit(1)


@db_cmds.command()
def list(
    sort_by: str = typer.Option("social_signal", "--sort", "-s", help="Sort by: social_signal, stars, age_days"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """List all analyzed repositories in the database."""
    if debug:
        log.set_debug(debug)

    valid_sort_fields = [
        "social_signal",
        "name",
        "username",
        "stars",
        "age_days",
        "last_analyzed",
        "commit_count",
    ]

    if sort_by not in valid_sort_fields:
        display.error(f"Invalid sort field '{sort_by}'. Valid options are: {', '.join(valid_sort_fields)}")
        raise typer.Exit(1)

    fields = [
        "group",
        "username",
        "name",
        "social_signal",
        "stars",
        "last_analyzed",
        "date_created",
    ]

    try:
        log.debug("Listing repositories")
        service = _init_services()
        log.debug("Getting all repositories")
        repos = service.get_all_repositories(sort_by=sort_by)
        log.debug("Displaying repositories")
        display.show_repository_list(repos, fields)
    except Exception as e:
        display.error(f"Error listing repositories: {e}\n{traceback.format_exc()}")
        raise typer.Exit(1)


@db_cmds.command()
def export(
    output_dir: str = typer.Option(".", "--output-dir", "-o", help="Directory to save the CSV file"),
    fields: List[str] = typer.Option(
        None,
        "--fields",
        "-f",
        help="Comma-separated list of fields to export. Default: all fields",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Export repository data to a CSV file.

    If no fields are specified, all fields will be exported.
    """
    if debug:
        log.set_debug(debug)
    try:
        db = get_db()

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Convert comma-separated string to list if needed
        if fields and isinstance(fields, str):
            fields = [f.strip() for f in fields.split(",")]

        filepath = db.export_to_csv(output_dir, fields)
        display.success(f"Successfully exported data to: {filepath}")
    except Exception as e:
        display.error(f"Error exporting database contents: {e}")
        raise typer.Exit(1)
