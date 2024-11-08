import time

from .gh_utils import GitHubAnalyzerImpl
from .gh_repo_dao import RepositoryDAO
from ..core.config import settings
from ..core.logger import log
from ..core.models import Repository


class RepositoryAnalyzer:
    def __init__(self, repository_dao: RepositoryDAO):
        self.repository_dao = repository_dao

    def analyze_repository(self, repo_path: str, force_update: bool = False) -> Repository:
        """Analyze repository and return metrics"""
        try:
            # Get existing metrics from database if not forcing update
            if not force_update:
                existing = self.repository_dao.get_by_path(repo_path)
                if existing:
                    return existing

            # Calculate new metrics
            analyzer = GitHubAnalyzerImpl(repo_path)
            metrics = analyzer.calculate_social_signal()

            # Save and return the metrics
            return self.repository_dao.save_metrics(metrics)
        except Exception as e:
            log.error(f"Error analyzing repository {repo_path}: {str(e)}")
            raise

    def _is_analysis_fresh(self, repo: Repository) -> bool:
        """Check if repository analysis is fresh enough"""
        cache_ttl = settings.database.CACHE_TTL_HOURS * 3600
        last_analyzed = getattr(repo, "last_analyzed", None) or 0
        return (time.time() - last_analyzed) < cache_ttl
