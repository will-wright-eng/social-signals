import time
from typing import List, Optional, Protocol
from dataclasses import fields, dataclass


@dataclass
class RepoMetrics:
    """Data class to store repository metrics"""

    name: str
    path: str
    username: str
    age_days: float
    update_frequency_days: float
    contributor_count: int
    stars: int
    commit_count: int
    lines_of_code: int
    open_issues: int
    social_signal: float
    group: Optional[str] = None
    id: Optional[int] = None
    last_analyzed: float = time.time()
    date_created: float = time.time()

    @classmethod
    def get_metric_fields(cls) -> List[str]:
        """Get list of metric field names"""
        return [f.name for f in fields(cls) if f.name != "id"]


class RepositoryStorage(Protocol):
    """Protocol defining repository storage interface"""

    def get_by_path(self, path: str) -> Optional[RepoMetrics]: ...
    def save_metrics(self, metrics: RepoMetrics) -> RepoMetrics: ...
    def get_all(self, sort_by: str = "social_signal") -> List[RepoMetrics]: ...


class GitHubAnalyzer(Protocol):
    """Protocol defining GitHub repository analyzer interface"""

    def get_repo_age(self) -> float: ...
    def get_update_frequency(self) -> float: ...
    def get_contributor_count(self) -> int: ...
    def get_stars(self) -> int: ...
    def get_commit_count(self) -> int: ...
    def get_lines_of_code(self) -> int: ...
    def get_open_issues(self) -> int: ...
    def calculate_social_signal(self) -> RepoMetrics: ...


class CommandRunner(Protocol):
    """Protocol defining command execution interface"""

    def run_command(self, command: List[str], cwd: str) -> str: ...


class MetricsNormalizer(Protocol):
    """Protocol defining metrics normalization interface"""

    def normalize_metrics(self, metrics: dict) -> dict: ...
    def calculate_score(self, normalized_metrics: dict) -> float: ...
