import json
import time
from typing import List

import rich
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, TextColumn, SpinnerColumn

from ..core.config import Config
from ..core.interfaces import RepoMetrics


class DisplayService:
    FIELD_LABELS = {
        "name": {
            "label": "Repository",
            "format": str,
            "width": 30,
            "justify": "left",
        },
        "username": {
            "label": "Username",
            "format": str,
            "width": 20,
            "justify": "left",
        },
        "age_days": {
            "label": "Age (days)",
            "format": lambda x: f"{x:.1f}",
            "width": 10,
            "justify": "right",
        },
        "update_frequency_days": {
            "label": "Update Freq",
            "format": lambda x: f"{x:.1f}",
            "width": 10,
            "justify": "right",
        },
        "contributor_count": {
            "label": "Contributors",
            "format": str,
            "width": 12,
            "justify": "right",
        },
        "stars": {
            "label": "Stars",
            "format": str,
            "width": 8,
            "justify": "right",
        },
        "commit_count": {
            "label": "Commits",
            "format": str,
            "width": 8,
            "justify": "right",
        },
        "social_signal": {
            "label": "Social Signal",
            "format": lambda x: f"{x:.1f}",
            "width": 12,
            "justify": "right",
        },
        "last_analyzed": {
            "label": "Last Analyzed",
            "format": lambda x: time.strftime("%Y-%m-%d", time.localtime(x)),
            "width": 12,
            "justify": "left",
        },
    }

    TABLE_STYLE = {
        "show_header": True,
        "header_style": "bold blue",
        "show_lines": True,
        "width": None,
        "min_width": 80,
        "box": rich.box.ROUNDED,
        "padding": (0, 1),
        "collapse_padding": True,
    }

    def __init__(self):
        self.console = Console()

    def error(self, message: str) -> None:
        """Display an error message"""
        self.console.print(f"[red]{message}[/red]")

    def warn(self, message: str) -> None:
        """Display a warning message"""
        self.console.print(f"[yellow]{message}[/yellow]")

    def _create_table(self, title: str) -> Table:
        """Create a consistently styled table"""
        return Table(title=title, **self.TABLE_STYLE)

    def show_analysis_results(self, results: List[RepoMetrics]) -> None:
        """Display analysis results in a table"""
        if not results:
            self.warn("No results to display")
            return

        fields_to_show = [
            "name",
            "username",
            "age_days",
            "update_frequency_days",
            "contributor_count",
            "stars",
            "commit_count",
            "social_signal",
        ]

        table = self._create_table("Repository Analysis Results")

        # Add columns using the complete field configuration
        for field in fields_to_show:
            field_config = self.FIELD_LABELS[field]
            table.add_column(
                field_config["label"],
                width=field_config["width"],
                justify=field_config["justify"],
                no_wrap=True,
            )

        # Add rows using the mapping
        for repo in results:
            row_data = [self.FIELD_LABELS[field]["format"](getattr(repo, field)) for field in fields_to_show]
            table.add_row(*row_data)

        self.console.print(table)

    def show_repository_list(self, repos: List[RepoMetrics]) -> None:
        """Display repository list in a table"""
        if not repos:
            self.warn("No repositories found in database")
            return

        fields_to_show = [
            "name",
            "username",
            "last_analyzed",
            "social_signal",
            "stars",
            "age_days",
            "update_frequency_days",
        ]

        table = self._create_table("Analyzed Repositories")

        # Add columns using the complete field configuration
        for field in fields_to_show:
            field_config = self.FIELD_LABELS[field]
            table.add_column(
                field_config["label"],
                width=field_config["width"],
                justify=field_config["justify"],
                no_wrap=True,
            )

        # Add rows using the mapping
        for metrics in repos:
            row_data = [self.FIELD_LABELS[field]["format"](getattr(metrics, field)) for field in fields_to_show]
            table.add_row(*row_data)

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

    def show_config(self, settings: Config, paths: dict) -> None:
        """Display configuration and paths"""
        # Use model_dump_json() to get a JSON string directly from the Pydantic model
        self.console.print_json(settings.model_dump_json())
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
