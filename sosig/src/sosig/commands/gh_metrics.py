import shutil
import traceback
from typing import List
from pathlib import Path

import typer

from ..core.logger import log
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
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """List all analyzed repositories in the database."""
    if debug:
        log.set_debug(debug)
    valid_sort_fields = ["social_signal", "name", "username", "stars", "age_days", "last_analyzed", "commit_count"]
    if sort_by not in valid_sort_fields:
        display.error(f"Invalid sort field '{sort_by}'. Valid options are: {', '.join(valid_sort_fields)}")
        raise typer.Exit(1)

    try:
        log.debug("Listing repositories")
        service = _init_services()
        log.debug("Getting all repositories")
        repos = service.get_all_repositories(sort_by=sort_by)
        log.debug("Displaying repositories")
        display.show_repository_list(repos)
    except Exception as e:
        display.error(f"Error listing repositories: {e}\n{traceback.format_exc()}")
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
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Analyze one or more GitHub repositories and store results."""
    if debug:
        log.set_debug(debug)
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        service = _init_services()
        with display.status("Analyzing repositories..."):
            results = service.analyze_repositories(repo_paths, workspace, force)
            _display_analysis_results(results)
    except Exception as e:
        display.error(f"Error analyzing repositories: {e}\n{traceback.format_exc()}")
    finally:
        if cleanup:
            _cleanup_path(workspace)
