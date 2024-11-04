import time

from ..core import models
from .gh_utils import GitHubAnalyzer
from .gh_repo_dao import RepositoryDAO
from ..core.config import settings
from ..core.logger import log


class RepositoryAnalyzer:
    def __init__(self, repository_dao: RepositoryDAO):
        self.repository_dao = repository_dao

    def analyze_repository(self, repo_path: str, force_update: bool = False) -> models.Repository:
        """Analyze a repository and store results in database"""
        existing_repo = self.repository_dao.get_by_path(repo_path)

        if existing_repo and not force_update:
            if self._is_analysis_fresh(existing_repo):
                log.info(f"Using cached analysis for {repo_path}")
                return existing_repo

        analyzer = GitHubAnalyzer(repo_path)
        metrics = analyzer.calculate_social_signal()

        return self.repository_dao.save_metrics(repo_path, metrics)

    def _is_analysis_fresh(self, repo: models.Repository) -> bool:
        """Check if repository analysis is fresh enough"""
        cache_ttl = settings.database.CACHE_TTL_HOURS * 3600
        return (time.time() - repo.last_analyzed) < cache_ttl
