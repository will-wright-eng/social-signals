import json
import time
import subprocess
from typing import List

from ..core.config import settings
from ..core.logger import log
from ..core.interfaces import (
    RepoMetrics,
    CommandRunner,
    GitHubAnalyzer,
    MetricsNormalizer,
)


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


class DefaultCommandRunner(CommandRunner):
    """Default implementation of command runner"""

    def run_command(self, command: List[str], cwd: str) -> str:
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitCommandError(
                message="Command execution failed",
                command=" ".join(command),
                stderr=e.stderr,
            )


class GitHubAnalyzerImpl(GitHubAnalyzer, MetricsNormalizer):
    """Implementation of GitHub repository analyzer"""

    def __init__(
        self,
        repo_path: str,
        command_runner: CommandRunner = None,
    ):
        self.repo_path = repo_path
        self.command_runner = command_runner or DefaultCommandRunner()
        self.config = settings
        self.weights = self.config.metrics.weights
        self.normalizers = self.config.metrics.normalizers

    def get_repo_age(self) -> float:
        """Calculate repository age in days"""
        first_commit_date = self.command_runner.run_command(
            [
                "git",
                "log",
                "--reverse",
                "--format=%ct",
                "--max-parents=0",
            ],
            self.repo_path,
        )
        creation_timestamp = float(first_commit_date)
        current_timestamp = time.time()
        return (current_timestamp - creation_timestamp) / (24 * 3600)

    def get_update_frequency(self) -> float:
        """Calculate average days between updates"""
        commit_dates = self.command_runner.run_command(
            [
                "git",
                "log",
                "--format=%ct",
            ],
            self.repo_path,
        ).splitlines()

        if len(commit_dates) < 2:
            return 0

        timestamps = [float(date) for date in commit_dates]
        total_days = (timestamps[0] - timestamps[-1]) / (24 * 3600)
        return total_days / (len(timestamps) - 1)

    def get_contributor_count(self) -> int:
        """Get number of unique contributors"""
        contributors = self.command_runner.run_command(
            [
                "git",
                "shortlog",
                "-s",
                "-n",
                "--all",
            ],
            self.repo_path,
        ).splitlines()
        return len(contributors)

    def get_stars(self) -> int:
        """Get repository star count using GitHub CLI"""
        try:
            repo_info = self.command_runner.run_command(
                ["gh", "repo", "view", "--json", "stargazerCount"],
                self.repo_path,
            )
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
        return len(self.command_runner.run_command(["git", "log", "--oneline"], self.repo_path).splitlines())

    def get_repo_username(self) -> str:
        """Get repository owner username using GitHub CLI"""
        try:
            repo_info = self.command_runner.run_command(
                ["gh", "repo", "view", "--json", "owner"],
                self.repo_path,
            )
            return json.loads(repo_info)["owner"]["login"]
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            msg = f"Could not fetch repository username: {str(e)}"
            log.warning(msg)
            raise GitHubAPIError(
                message=msg,
                endpoint="repo view",
            )

    def get_lines_of_code(self) -> int:
        """Get total lines of code in the repository"""
        try:
            # Use a simpler command that doesn't rely on pipes
            files_output = self.command_runner.run_command(
                ["git", "ls-files"],
                self.repo_path,
            )
            total_lines = 0
            for file in files_output.splitlines():
                try:
                    lines = self.command_runner.run_command(
                        ["wc", "-l", file],
                        self.repo_path,
                    )
                    total_lines += int(lines.split()[0])
                except (ValueError, IndexError, GitCommandError):
                    continue
            return total_lines
        except Exception as e:
            log.warning(f"Could not fetch lines of code: {str(e)}")
            return 0

    def get_open_issues(self) -> int:
        """Get number of open issues using GitHub CLI"""
        try:
            repo_info = self.command_runner.run_command(
                ["gh", "repo", "view", "--json", "issues"],
                self.repo_path,
            )
            data = json.loads(repo_info)
            log.debug(f"Open issues: {data}")
            if not isinstance(data, dict):
                log.warning("Unexpected API response format: %s", str(data))
                return 0
            issues = data.get("issues", [])
            if not isinstance(issues, list):
                return len([issue for issue in issues if isinstance(issue, dict) and issue.get("state") == "OPEN"])
            elif isinstance(issues, dict):
                return issues.get("totalCount", 0)
            else:
                return 0
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            log.warning("Could not fetch open issues: %s", str(e))
            return 0
        except Exception as e:
            log.warning("Unexpected error fetching open issues: %s", str(e))
            return 0

    def _normalize_metrics(self, metrics: dict) -> dict:
        """Normalize metrics to 0-1 scale"""
        normalized = {
            "age": min(metrics["age_days"] / self.normalizers["max_age_days"], 1.0),
            "update_frequency": 1.0
            - min(
                metrics["update_frequency"] / self.normalizers["max_update_frequency_days"],
                1.0,
            ),
            "contributors": min(
                metrics["contributor_count"] / self.normalizers["max_contributors"],
                1.0,
            ),
            "stars": min(metrics["stars"] / self.normalizers["max_stars"], 1.0),
            "commits": min(metrics["commit_count"] / self.normalizers["max_commits"], 1.0),
            "lines_of_code": min(metrics["lines_of_code"] / self.normalizers["max_lines_of_code"], 1.0),
            "open_issues": min(metrics["open_issues"] / self.normalizers["max_open_issues"], 1.0),
        }
        return normalized

    def _calculate_score(self, normalized_metrics: dict) -> float:
        """Calculate weighted social signal score"""
        return sum(self.weights[key] * value for key, value in normalized_metrics.items()) * 100

    def calculate_social_signal(self) -> RepoMetrics:
        """Perform complete repository analysis and calculate social signal score"""
        try:
            raw_metrics = {
                "age_days": self.get_repo_age(),
                "update_frequency": self.get_update_frequency(),
                "contributor_count": self.get_contributor_count(),
                "stars": self.get_stars(),
                "commit_count": self.get_commit_count(),
                "lines_of_code": self.get_lines_of_code(),
                "open_issues": self.get_open_issues(),
            }

            normalized = self._normalize_metrics(raw_metrics)
            social_signal = self._calculate_score(normalized)

            return RepoMetrics(
                name=self.repo_path.split("/")[-1],
                path=self.repo_path,
                username=self.get_repo_username(),
                age_days=raw_metrics["age_days"],
                update_frequency_days=raw_metrics["update_frequency"],
                contributor_count=raw_metrics["contributor_count"],
                stars=raw_metrics["stars"],
                commit_count=raw_metrics["commit_count"],
                lines_of_code=raw_metrics["lines_of_code"],
                open_issues=raw_metrics["open_issues"],
                social_signal=social_signal,
                last_analyzed=time.time(),
            )

        except (GitCommandError, GitHubAPIError) as e:
            log.error(f"Error analyzing repository: {str(e)}")
            raise
