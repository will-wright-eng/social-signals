import shutil
from typing import List
from pathlib import Path

import typer
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, TextColumn, SpinnerColumn

from ..core import db, models
from ..utils.gh_analyzer import RepositoryAnalyzer
from ..utils.gh_repo_dao import RepositoryDAO

gh_cmds = typer.Typer()
console = Console()


@gh_cmds.callback()
def callback():
    """
    Analyze GitHub repositories for social signals and community health metrics.
    """
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
    """
    Analyze one or more GitHub repositories and store results.
    """
    # Create workspace directory if it doesn't exist
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        Session = db.init_db()
        session = Session()

        repository_dao = RepositoryDAO(session)
        analyzer = RepositoryAnalyzer(repository_dao)

        results = []
        with console.status("Analyzing repositories...") as status:
            for path in repo_paths:
                repo_path = workspace / Path(path).name
                try:
                    # Copy or clone repository to workspace
                    if not repo_path.exists() or force:
                        status.update(f"Preparing {path}...")
                        if Path(path).exists():
                            shutil.copytree(path, repo_path, dirs_exist_ok=True)
                        else:
                            _run_command(["gh", "repo", "clone", path, str(repo_path)])

                    # Analyze repository
                    repo = analyzer.analyze_repository(str(repo_path), force_update=force)
                    results.append(repo)

                except Exception as e:
                    console.print(f"[red]Error analyzing {path}: {str(e)}[/red]")
                    # Clean up failed repo immediately
                    if cleanup and repo_path.exists():
                        try:
                            shutil.rmtree(repo_path)
                        except Exception as cleanup_err:
                            console.print(f"[yellow]Warning: Could not clean up {repo_path}: {cleanup_err}[/yellow]")

        _display_analysis_results(results)

    finally:
        # Clean up the workspace if requested
        if cleanup and workspace.exists():
            try:
                console.print("Cleaning up workspace...")
                shutil.rmtree(workspace)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not clean up workspace: {e}[/yellow]")


@gh_cmds.command()
def list(
    sort_by: str = typer.Option("social_signal", "--sort", "-s", help="Sort by: social_signal, stars, age_days"),
):
    """
    List all analyzed repositories in the database.
    """
    Session = db.init_db()
    session = Session()

    query = session.query(models.Repository)
    if hasattr(models.Repository, sort_by):
        query = query.order_by(getattr(models.Repository, sort_by).desc())

    repos = query.all()

    table = Table(title="Analyzed Repositories")
    table.add_column("Repository")
    table.add_column("Last Analyzed")
    table.add_column("Social Signal")
    table.add_column("Stars")

    for repo in repos:
        table.add_row(
            repo.name,
            repo.last_analyzed.strftime("%Y-%m-%d %H:%M"),
            f"{repo.social_signal:.1f}",
            str(repo.stars),
        )

    console.print(table)


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
    """
    Analyze repositories from a file containing GitHub URLs.
    """
    if not urls_file.exists():
        console.print(f"[red]Error: File not found: {urls_file}[/red]")
        raise typer.Exit(1)

    # Create workspace directory if it doesn't exist
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        # Read URLs from file
        urls = urls_file.read_text().splitlines()
        urls = [url.strip() for url in urls if url.strip()]

        if not urls:
            console.print("[yellow]No URLs found in file[/yellow]")
            raise typer.Exit(0)

        # Initialize database
        Session = db.init_db()
        session = Session()

        repository_dao = RepositoryDAO(session)
        analyzer = RepositoryAnalyzer(repository_dao)

        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for url in progress.track(urls, description="Processing repositories..."):
                repo_path = None
                try:
                    # Extract repo name from URL
                    repo_name = url.rstrip("/").split("/")[-1]
                    repo_path = workspace / repo_name

                    # Clone repository if it doesn't exist
                    if not repo_path.exists() or force:
                        progress.log(f"Cloning {url}...")
                        _run_command(["gh", "repo", "clone", url, str(repo_path)])

                    # Analyze repository
                    repo = analyzer.analyze_repository(str(repo_path), force_update=force)
                    results.append(repo)

                except Exception as e:
                    progress.log(f"[red]Error processing {url}: {str(e)}[/red]")
                    # Clean up failed repo immediately
                    if cleanup and repo_path and repo_path.exists():
                        try:
                            shutil.rmtree(repo_path)
                        except Exception as cleanup_err:
                            progress.log(f"[yellow]Warning: Could not clean up {repo_path}: {cleanup_err}[/yellow]")

        _display_analysis_results(results)

    finally:
        # Clean up the entire workspace if requested
        if cleanup and workspace.exists():
            try:
                console.print("Cleaning up workspace...")
                shutil.rmtree(workspace)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not clean up workspace: {e}[/yellow]")


def _display_analysis_results(results: List[models.Repository]):
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


def _run_command(command: List[str]) -> str:
    """Helper function to run shell commands"""
    import subprocess

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Command failed: {' '.join(command)}\nError: {e.stderr}")
