import shutil
from typing import List
from pathlib import Path

import typer
from rich.progress import Progress, TextColumn, SpinnerColumn

from ..core.interfaces import RepoMetrics
from ..utils.gh_analyzer import RepositoryAnalyzer
from ..utils.gh_repo_dao import RepositoryDAO
from ..utils.display_service import display
from ..utils.gh_repo_service import RepositoryService

gh_cmds = typer.Typer()


def _init_services():
    """Initialize services"""
    repository_dao = RepositoryDAO()
    analyzer = RepositoryAnalyzer(repository_dao)
    return RepositoryService(repository_dao, analyzer)


def _display_analysis_results(results: List[RepoMetrics]):
    """Helper function to display analysis results in a table"""
    display.show_analysis_results(results)


def _cleanup_path(path: Path) -> None:
    """Helper function to safely clean up a path"""
    try:
        if path.exists():
            shutil.rmtree(path)
    except Exception as e:
        display.warn(f"Could not clean up {path}: {e}")


@gh_cmds.command()
def list(
    sort_by: str = typer.Option("social_signal", "--sort", "-s", help="Sort by: social_signal, stars, age_days"),
):
    """List all analyzed repositories in the database."""
    valid_sort_fields = ["social_signal", "stars", "age_days", "last_analyzed", "commit_count"]
    if sort_by not in valid_sort_fields:
        display.error(f"Invalid sort field '{sort_by}'. Valid options are: {', '.join(valid_sort_fields)}")
        raise typer.Exit(1)

    try:
        service = _init_services()
        repos = service.get_all_repositories(sort_by=sort_by)
        display.show_repository_list(repos)
    except Exception as e:
        display.error(f"Error listing repositories: {e}")
        raise typer.Exit(1)


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
        service = _init_services()
        with display.status("Analyzing repositories..."):
            results = service.analyze_repositories(repo_paths, workspace, force)
            _display_analysis_results(results)
    finally:
        if cleanup:
            _cleanup_path(workspace)


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
        display.error(f"Error: File not found: {urls_file}")
        raise typer.Exit(1)

    workspace.mkdir(parents=True, exist_ok=True)

    try:
        urls = [url.strip() for url in urls_file.read_text().splitlines() if url.strip()]
        if not urls:
            display.warn("No URLs found in file")
            raise typer.Exit(0)

        service = _init_services()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            display.console,
        ) as progress:
            progress.add_task("Processing repositories...", total=len(urls))
            results = service.analyze_repositories(urls, workspace, force)
            _display_analysis_results(results)

    finally:
        if cleanup:
            _cleanup_path(workspace)
