import typer

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
def dump(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Dump all repository data from the database."""
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
