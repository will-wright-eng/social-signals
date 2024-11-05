import time
from typing import List, Optional

from ..core.db import get_db
from ..core.models import Repository
from ..utils.gh_utils import RepoMetrics


class RepositoryDAO:
    """Data Access Object for Repository operations"""

    def __init__(self):
        self.db = get_db()

    def get_by_path(self, path: str) -> Optional[Repository]:
        """Get repository by path."""
        with self.db.get_session() as session:
            return session.query(Repository).filter_by(path=path).first()

    def get_all(self, sort_by: str = "social_signal") -> List[Repository]:
        """Get all repositories with optional sorting."""
        with self.db.get_session() as session:
            query = session.query(Repository)
            if hasattr(Repository, sort_by):
                query = query.order_by(getattr(Repository, sort_by).desc())
            return query.all()

    def save_metrics(self, repo_path: str, metrics: RepoMetrics) -> Repository:
        """Save or update repository metrics."""
        with self.db.get_session() as session:
            existing = session.query(Repository).filter_by(path=repo_path).first()

            if existing:
                self._update_repository(existing, metrics)
            else:
                existing = self._create_repository(repo_path, metrics)
                session.add(existing)

            return existing

    def _update_repository(self, repo: Repository, metrics: RepoMetrics) -> None:
        """Update repository with new metrics."""
        repo.age_days = metrics.age_days
        repo.update_frequency_days = metrics.update_frequency_days
        repo.contributor_count = metrics.contributor_count
        repo.stars = metrics.stars
        repo.commit_count = metrics.commit_count
        repo.social_signal = metrics.social_signal
        repo.last_analyzed = time.time()

    def _create_repository(self, repo_path: str, metrics: RepoMetrics) -> Repository:
        """Create new repository from metrics."""
        return Repository(
            name=metrics.name,
            path=repo_path,
            age_days=metrics.age_days,
            update_frequency_days=metrics.update_frequency_days,
            contributor_count=metrics.contributor_count,
            stars=metrics.stars,
            commit_count=metrics.commit_count,
            social_signal=metrics.social_signal,
            last_analyzed=time.time(),
        )
