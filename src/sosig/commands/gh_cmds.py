import shutil
import traceback
from typing import List
from pathlib import Path

import typer

from .common import _init_services
from ..core.config import settings
from ..core.logger import log
from ..core.interfaces import RepoMetrics
from ..utils.display_service import display

gh_cmds = typer.Typer()


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
def analyze(
    repo_paths: List[str] = typer.Argument(..., help="Paths to local git repositories"),
    workspace: Path = typer.Option(
        settings.workspace,
        help="Directory for cloning repositories",
    ),
    group: str = typer.Option(None, "--group", "-g", help="Group name for the repositories"),
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
            results = service.analyze_repositories(repo_paths, workspace, force, group)
            _display_analysis_results(results)
    except Exception as e:
        display.error(f"Error analyzing repositories: {e}\n{traceback.format_exc()}")
    finally:
        if cleanup:
            _cleanup_path(workspace)
