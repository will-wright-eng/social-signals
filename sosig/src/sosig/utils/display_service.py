import json
import time
from typing import List

from rich.table import Table
from rich.console import Console
from rich.progress import Progress, TextColumn, SpinnerColumn

from ..core.interfaces import RepoMetrics


class DisplayService:
    def __init__(self):
        self.console = Console()

    def error(self, message: str) -> None:
        """Display an error message"""
        self.console.print(f"[red]{message}[/red]")

    def warn(self, message: str) -> None:
        """Display a warning message"""
        self.console.print(f"[yellow]{message}[/yellow]")

    def show_analysis_results(self, results: List[RepoMetrics]) -> None:
        """Display analysis results in a table"""
        if not results:
            self.warn("No results to display")
            return

        table = Table(title="Repository Analysis Results")
        table.add_column("Repository")
        table.add_column("Username")
        table.add_column("Age (days)")
        table.add_column("Update Freq")
        table.add_column("Contributors")
        table.add_column("Stars")
        table.add_column("Commits")
        table.add_column("Social Signal")

        for repo in results:
            table.add_row(
                repo.name,
                repo.username,
                f"{repo.age_days:.1f}",
                f"{repo.update_frequency_days:.1f}",
                str(repo.contributor_count),
                str(repo.stars),
                str(repo.commit_count),
                f"{repo.social_signal:.1f}",
            )

        self.console.print(table)

    def show_repository_list(self, repos: List[RepoMetrics]) -> None:
        """Display repository list in a table"""
        if not repos:
            self.warn("No repositories found in database")
            return

        table = Table(title="Analyzed Repositories")
        table.add_column("Repository")
        table.add_column("Username")
        table.add_column("Last Analyzed")
        table.add_column("Social Signal")
        table.add_column("Stars")
        table.add_column("Age (days)")
        table.add_column("Update Freq")

        for metrics in repos:
            analyzed_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(metrics.last_analyzed))
            table.add_row(
                metrics.name,
                metrics.username,
                analyzed_time,
                f"{metrics.social_signal:.1f}",
                str(metrics.stars),
                f"{metrics.age_days:.1f}",
                f"{metrics.update_frequency_days:.1f}",
            )

        self.console.print(table)

    def create_progress(self) -> Progress:
        """Create and return a progress bar"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )

    def status(self, message: str):
        """Create and return a status context"""
        return self.console.status(message)

    def success(self, message: str) -> None:
        """Display a success message"""
        self.console.print(f"[green]{message}[/green]")

    def show_config(self, config: dict, paths: dict) -> None:
        """Display configuration and paths"""
        self.console.print_json(json.dumps(config, indent=2))
        self.console.print("[bold]Application Paths:[/bold]")
        for key, value in paths.items():
            self.console.print(f"{key}: {value}")

    def show_db_stats(self, stats: dict) -> None:
        """Display database statistics"""
        table = Table(title="Database Statistics")
        table.add_column("Metric")
        table.add_column("Value")

        table.add_row("Total Repositories", str(stats["total_repos"]))
        table.add_row("Average Social Signal", f"{stats['avg_signal']:.2f}")
        table.add_row("Average Stars", f"{stats['avg_stars']:.1f}")

        self.console.print(table)

    def info(self, message: str) -> None:
        """Display an info message"""
        self.console.print(message)


display = DisplayService()
