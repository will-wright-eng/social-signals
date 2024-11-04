import typer
from rich.table import Table
from rich.console import Console

from ..core import db, config, models
from ..utils.gh_repo_dao import RepositoryDAO
from ..utils.ghmetrics_analyzer import RepositoryAnalyzer

ghmetrics_cmds = typer.Typer()
console = Console()


@ghmetrics_cmds.callback()
def callback():
    """
    Analyze GitHub repositories for social signals and community health metrics.
    """
    pass


@ghmetrics_cmds.command()
def analyze(
    repo_paths: list[str] = typer.Argument(..., help="Paths to local git repositories"),
    force: bool = typer.Option(False, "--force", "-f", help="Force reanalysis of repositories"),
    db_path: str = typer.Option(None, "--db", help="SQLite database path"),
):
    """
    Analyze one or more GitHub repositories and store results.
    """
    db_uri = db_path or config.settings.database.URI
    Session = db.init_db(db_uri)
    session = Session()

    repository_dao = RepositoryDAO(session)
    analyzer = RepositoryAnalyzer(repository_dao)

    with console.status("Analyzing repositories..."):
        results = []
        for path in repo_paths:
            try:
                repo = analyzer.analyze_repository(path, force_update=force)
                results.append(repo)
            except Exception as e:
                console.print(f"[red]Error analyzing {path}: {str(e)}[/red]")

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


@ghmetrics_cmds.command()
def list_repos(
    db_path: str = typer.Option(None, "--db", help="SQLite database path"),
    sort_by: str = typer.Option("social_signal", "--sort", "-s", help="Sort by: social_signal, stars, age_days"),
):
    """
    List all analyzed repositories in the database.
    """
    db_uri = db_path or config.settings.database.URI
    Session = db.init_db(db_uri)
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


# if __name__ == "__main__":
#     # Example usage
#     repos = ["/path/to/repo1", "/path/to/repo2"]
#     metrics = analyze_repos(repos)

#     for repo in metrics:
#         print(f"\nRepository: {repo.name}")
#         print(f"Age: {repo.age_days:.1f} days")
#         print(f"Update Frequency: {repo.update_frequency_days:.1f} days")
#         print(f"Contributors: {repo.contributor_count}")
#         print(f"Stars: {repo.stars}")
#         print(f"Commits: {repo.commit_count}")
#         print(f"Social Signal Score: {repo.social_signal:.1f}/100")
