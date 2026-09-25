import shutil
from typing import List, Optional
from pathlib import Path

from ..core.logger import log
from ..utils.gh_utils import GitHubAPIError, GitCommandError
from ..core.interfaces import RepoMetrics
from ..utils.gh_analyzer import RepositoryAnalyzer
from ..utils.gh_repo_dao import RepositoryDAO


class RepositoryService:
    """Service class to handle repository analysis operations"""

    def __init__(self, repository_dao: RepositoryDAO, analyzer: RepositoryAnalyzer):
        self.repository_dao = repository_dao
        self.analyzer = analyzer

    def analyze_repositories(
        self,
        paths: List[str],
        workspace: Path,
        force: bool = False,
        group: Optional[str] = None,
    ) -> List[RepoMetrics]:
        """Analyze multiple repositories and return their metrics"""
        results = []
        for path in paths:
            try:
                repo_path = workspace / Path(path).name
                metrics = self._analyze_single_repo(path, repo_path, force, group)
                if metrics:
                    results.append(metrics)
            except (GitCommandError, GitHubAPIError) as e:
                log.error(f"Error analyzing {path}: {str(e)}")
                continue
        return results

    def get_all_repositories(self, sort_by: str = "social_signal") -> List[RepoMetrics]:
        """Get all repositories sorted by the specified field"""
        return [repo.to_metrics() for repo in self.repository_dao.get_all(sort_by=sort_by)]

    def _analyze_single_repo(
        self,
        source_path: str,
        target_path: Path,
        force: bool,
        group: Optional[str] = None,
    ) -> Optional[RepoMetrics]:
        """Analyze a single repository and return its metrics"""
        if not target_path.exists() or force:
            self._prepare_repository(source_path, target_path)

        metrics = self.analyzer.analyze_repository(str(target_path), force_update=force, group=group)
        return metrics

    def _prepare_repository(self, source: str, target: Path) -> None:
        """Prepare repository for analysis by copying or cloning"""
        if Path(source).exists():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            self._clone_repository(source, target)

    @staticmethod
    def _clone_repository(repo_url: str, target_path: Path) -> None:
        """Clone repository using GitHub CLI"""
        from subprocess import CalledProcessError, run

        try:
            run(
                ["gh", "repo", "clone", repo_url, str(target_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        except CalledProcessError as e:
            raise GitCommandError(
                message="Failed to clone repository",
                command=f"gh repo clone {repo_url}",
                stderr=e.stderr,
            )
