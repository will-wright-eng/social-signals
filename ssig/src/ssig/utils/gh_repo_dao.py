import time
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import Repository
from ..utils.ghmetrics_utils import RepoMetrics


class RepositoryDAO:
    """Data Access Object for Repository operations"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_path(self, path: str) -> Optional[Repository]:
        return self.session.query(Repository).filter_by(path=path).first()

    def get_all(self, sort_by: str = "social_signal") -> List[Repository]:
        query = self.session.query(Repository)
        if hasattr(Repository, sort_by):
            query = query.order_by(getattr(Repository, sort_by).desc())
        return query.all()

    def save_metrics(self, repo_path: str, metrics: RepoMetrics) -> Repository:
        existing = self.get_by_path(repo_path)

        if existing:
            self._update_repository(existing, metrics)
        else:
            existing = self._create_repository(repo_path, metrics)

        self.session.commit()
        return existing

    def _update_repository(self, repo: Repository, metrics: RepoMetrics) -> None:
        repo.age_days = metrics.age_days
        repo.update_frequency_days = metrics.update_frequency_days
        repo.contributor_count = metrics.contributor_count
        repo.stars = metrics.stars
        repo.commit_count = metrics.commit_count
        repo.social_signal = metrics.social_signal
        repo.last_analyzed = time.time()

    def _create_repository(self, repo_path: str, metrics: RepoMetrics) -> Repository:
        repo = Repository(
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
        self.session.add(repo)
        return repo
