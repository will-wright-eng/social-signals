import time
import shutil
from typing import List
from pathlib import Path

import typer
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, TextColumn, SpinnerColumn

from ..core import db
from ..core.interfaces import RepoMetrics
from ..utils.gh_analyzer import RepositoryAnalyzer
from ..utils.gh_repo_dao import RepositoryDAO
from ..utils.gh_repo_service import RepositoryService

gh_cmds = typer.Typer()
console = Console()


def _init_services():
    """Initialize database session and services"""
    Session = db.init_db()
    session = Session()
    repository_dao = RepositoryDAO(session)
    analyzer = RepositoryAnalyzer(repository_dao)
    return RepositoryService(repository_dao, analyzer), session


def _display_analysis_results(results: List[RepoMetrics]):
    """Helper function to display analysis results in a table"""
    if not results:
        console.print("[yellow]No results to display[/yellow]")
        return

    table = Table(title="Repository Analysis Results")
    table.add_column("Repository")
    table.add_column("Age (days)")
    table.add_column("Update Freq")
    table.add_column("Contributors")
    table.add_column("Stars")
    table.add_column("Commits")
    table.add_column("Social Signal")

    for repo in results:
        table.add_row(
            repo.name,
            f"{repo.age_days:.1f}",
            f"{repo.update_frequency_days:.1f}",
            str(repo.contributor_count),
            str(repo.stars),
            str(repo.commit_count),
            f"{repo.social_signal:.1f}",
        )

    console.print(table)


def _cleanup_path(path: Path) -> None:
    """Helper function to safely clean up a path"""
    try:
        if path.exists():
            shutil.rmtree(path)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not clean up {path}: {e}[/yellow]")


@gh_cmds.callback()
def callback():
    """Analyze GitHub repositories for social signals and community health metrics."""
    pass


@gh_cmds.command()
def analyze(
    repo_paths: List[str] = typer.Argument(..., help="Paths to local git repositories"),
    workspace: Path = typer.Option(
        Path.home() / ".local" / "share" / "ssig" / "workspace",
        help="Directory for cloning repositories",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force reanalysis of repositories"),
    cleanup: bool = typer.Option(True, "--cleanup/--no-cleanup", help="Clean up repositories after analysis"),
):
    """Analyze one or more GitHub repositories and store results."""
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        service, session = _init_services()
        with console.status("Analyzing repositories..."):
            results = service.analyze_repositories(repo_paths, workspace, force)
            _display_analysis_results(results)
    finally:
        session.close()
        if cleanup:
            _cleanup_path(workspace)


@gh_cmds.command()
def list(
    sort_by: str = typer.Option("social_signal", "--sort", "-s", help="Sort by: social_signal, stars, age_days"),
):
    """List all analyzed repositories in the database."""
    valid_sort_fields = ["social_signal", "stars", "age_days", "last_analyzed", "commit_count"]
    if sort_by not in valid_sort_fields:
        console.print(
            f"[red]Error: Invalid sort field '{sort_by}'. Valid options are: {', '.join(valid_sort_fields)}[/red]",
        )
        raise typer.Exit(1)

    try:
        service, session = _init_services()
        repos = service.get_all_repositories(sort_by=sort_by)

        if not repos:
            console.print("[yellow]No repositories found in database[/yellow]")
            return

        table = Table(title="Analyzed Repositories")
        table.add_column("Repository")
        table.add_column("Last Analyzed")
        table.add_column("Social Signal")
        table.add_column("Stars")
        table.add_column("Age (days)")
        table.add_column("Update Freq")

        for metrics in repos:
            analyzed_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(metrics.last_analyzed))
            table.add_row(
                metrics.name,
                analyzed_time,
                f"{metrics.social_signal:.1f}",
                str(metrics.stars),
                f"{metrics.age_days:.1f}",
                f"{metrics.update_frequency_days:.1f}",
            )

        console.print(table)

    finally:
        session.close()


@gh_cmds.command()
def analyze_from_file(
    urls_file: Path = typer.Argument(..., help="Path to file containing repository URLs"),
    workspace: Path = typer.Option(
        Path.home() / ".local" / "share" / "ssig" / "workspace",
        help="Directory for cloning repositories",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force reanalysis of repositories"),
    cleanup: bool = typer.Option(True, "--cleanup/--no-cleanup", help="Clean up cloned repositories after analysis"),
):
    """Analyze repositories from a file containing GitHub URLs."""
    if not urls_file.exists():
        console.print(f"[red]Error: File not found: {urls_file}[/red]")
        raise typer.Exit(1)

    workspace.mkdir(parents=True, exist_ok=True)

    try:
        urls = [url.strip() for url in urls_file.read_text().splitlines() if url.strip()]
        if not urls:
            console.print("[yellow]No URLs found in file[/yellow]")
            raise typer.Exit(0)

        service, session = _init_services()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Processing repositories...", total=len(urls))
            results = service.analyze_repositories(urls, workspace, force)
            _display_analysis_results(results)

    finally:
        session.close()
        if cleanup:
            _cleanup_path(workspace)
