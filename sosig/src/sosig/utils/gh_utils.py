import json
import time
import subprocess
from typing import List, Optional, Protocol
from dataclasses import dataclass

from ..core.logger import log


class GitCommandError(Exception):
    """Raised when a git command fails"""

    def __init__(self, message: str, command: str = None, stderr: str = None):
        self.command = command
        self.stderr = stderr
        super().__init__(
            f"Git command failed: {message}"
            + (f"\nCommand: {command}" if command else "")
            + (f"\nError: {stderr}" if stderr else ""),
        )


class GitHubAPIError(Exception):
    """Raised when GitHub API operations fail"""

    def __init__(self, message: str, endpoint: str = None, status_code: int = None):
        self.endpoint = endpoint
        self.status_code = status_code
        super().__init__(
            f"GitHub API error: {message}"
            + (f"\nEndpoint: {endpoint}" if endpoint else "")
            + (f"\nStatus Code: {status_code}" if status_code else ""),
        )


@dataclass
class RepoMetrics:
    """Data class to store repository metrics"""

    name: str
    path: str
    age_days: float
    update_frequency_days: float
    contributor_count: int
    stars: int
    commit_count: int
    social_signal: float
    last_analyzed: float = 0.0


class GitHubAnalyzer:
    """Analyzes GitHub repositories to calculate social signal metrics"""

    # Normalization and weight constants
    MAX_AGE_DAYS = 1825  # 5 years
    MAX_UPDATE_FREQ = 30
    MAX_CONTRIBUTORS = 50
    MAX_STARS = 1000
    MAX_COMMITS = 1000

    WEIGHTS = {
        "age": 0.2,
        "update_frequency": 0.3,
        "contributors": 0.2,
        "stars": 0.2,
        "commits": 0.1,
    }

    def __init__(self, repo_path: str):
        """Initialize analyzer with local repository path"""
        self.repo_path = repo_path

    def _run_command(self, command: List[str]) -> str:
        """Execute a shell command and return its output"""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            log.error(f"Command failed: {' '.join(command)}")
            log.error(f"Error: {e.stderr}")
            raise GitCommandError(
                message="Command execution failed",
                command=" ".join(command),
                stderr=e.stderr,
            )

    def get_repo_age(self) -> float:
        """Calculate repository age in days"""
        first_commit_date = self._run_command(
            [
                "git",
                "log",
                "--reverse",
                "--format=%ct",
                "--max-parents=0",
            ],
        )
        creation_timestamp = float(first_commit_date)
        current_timestamp = time.time()
        return (current_timestamp - creation_timestamp) / (24 * 3600)

    def get_update_frequency(self) -> float:
        """Calculate average days between updates"""
        commit_dates = self._run_command(
            [
                "git",
                "log",
                "--format=%ct",
            ],
        ).splitlines()

        if len(commit_dates) < 2:
            return 0

        timestamps = [float(date) for date in commit_dates]
        total_days = (timestamps[0] - timestamps[-1]) / (24 * 3600)
        return total_days / (len(timestamps) - 1)

    def get_contributor_count(self) -> int:
        """Get number of unique contributors"""
        contributors = self._run_command(
            [
                "git",
                "shortlog",
                "-s",
                "-n",
                "--all",
            ],
        ).splitlines()
        return len(contributors)

    def get_stars(self) -> int:
        """Get repository star count using GitHub CLI"""
        try:
            repo_info = self._run_command(["gh", "repo", "view", "--json", "stargazerCount"])
            return json.loads(repo_info)["stargazerCount"]
        except subprocess.CalledProcessError as e:
            msg = f"Could not fetch star count: {str(e)}"
            log.warning(msg)
            raise GitHubAPIError(
                message=msg,
                endpoint="repo view",
                status_code=e.returncode,
            )
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON response from GitHub API: {str(e)}"
            log.warning(msg)
            raise GitHubAPIError(
                message=msg,
                endpoint="repo view",
            )
        except KeyError as e:
            msg = f"Star count not found in GitHub API response: {str(e)}"
            log.warning(msg)
            raise GitHubAPIError(
                message=msg,
                endpoint="repo view",
            )

    def get_commit_count(self) -> int:
        """Get total number of commits"""
        return len(self._run_command(["git", "log", "--oneline"]).splitlines())

    def _normalize_metrics(self, metrics: dict) -> dict:
        """Normalize metrics to 0-1 scale"""
        return {
            "age": min(metrics["age_days"] / self.MAX_AGE_DAYS, 1.0),
            "update_frequency": 1.0 - min(metrics["update_frequency"] / self.MAX_UPDATE_FREQ, 1.0),
            "contributors": min(metrics["contributor_count"] / self.MAX_CONTRIBUTORS, 1.0),
            "stars": min(metrics["stars"] / self.MAX_STARS, 1.0),
            "commits": min(metrics["commit_count"] / self.MAX_COMMITS, 1.0),
        }

    def _calculate_score(self, normalized_metrics: dict) -> float:
        """Calculate weighted social signal score"""
        return sum(self.WEIGHTS[key] * value for key, value in normalized_metrics.items()) * 100

    def analyze(self) -> RepoMetrics:
        """Perform complete repository analysis"""
        try:
            raw_metrics = {
                "age_days": self.get_repo_age(),
                "update_frequency": self.get_update_frequency(),
                "contributor_count": self.get_contributor_count(),
                "stars": self.get_stars(),
                "commit_count": self.get_commit_count(),
            }

            normalized = self._normalize_metrics(raw_metrics)
            social_signal = self._calculate_score(normalized)

            return RepoMetrics(
                name=self.repo_path.split("/")[-1],
                path=self.repo_path,
                age_days=raw_metrics["age_days"],
                update_frequency_days=raw_metrics["update_frequency"],
                contributor_count=raw_metrics["contributor_count"],
                stars=raw_metrics["stars"],
                commit_count=raw_metrics["commit_count"],
                social_signal=social_signal,
                last_analyzed=time.time(),
            )

        except (GitCommandError, GitHubAPIError) as e:
            log.error(f"Error analyzing repository: {str(e)}")
            raise


class RepositoryStorage(Protocol):
    """Protocol defining repository storage interface"""

    def get_by_path(self, path: str) -> Optional[RepoMetrics]: ...
    def save_metrics(self, metrics: RepoMetrics) -> RepoMetrics: ...
    def get_all(self, sort_by: str = "social_signal") -> List[RepoMetrics]: ...
