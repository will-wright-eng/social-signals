import time
from typing import List, Optional

from ..core.db import get_db
from ..core.logger import log
from ..core.models import Repository
from ..core.interfaces import RepoMetrics


class RepositoryDAO:
    """Data Access Object for Repository operations"""

    def __init__(self):
        self.db = get_db()

    def get_by_path(self, path: str) -> Optional[RepoMetrics]:
        """Get repository by path."""
        with self.db.get_session() as session:
            repo = session.query(Repository).filter_by(path=path).first()
            if repo:
                # Convert to RepoMetrics directly to avoid detached instance issues
                return repo.to_metrics()
            return None

    def get_all(self, sort_by: str = "social_signal") -> List[RepoMetrics]:
        """Get all repositories with optional sorting."""
        with self.db.get_session() as session:
            query = session.query(Repository)
            if hasattr(Repository, sort_by):
                query = query.order_by(getattr(Repository, sort_by).desc())
            # Create detached copies of all repositories
            return [
                Repository(
                    **{k: v for k, v in repo.__dict__.items() if not k.startswith("_")},
                )
                for repo in query.all()
            ]

    def save_metrics(self, metrics: RepoMetrics) -> RepoMetrics:
        """Save or update repository metrics."""
        with self.db.get_session() as session:
            existing = session.query(Repository).filter_by(path=metrics.path).first()

            if existing:
                log.debug(f"Updating existing repository: {existing.path}")
                # Update existing repository
                for field in RepoMetrics.get_metric_fields():
                    # Don't update date_created for existing records
                    if field != "date_created":
                        setattr(existing, field, getattr(metrics, field))
                repo = existing
            else:
                # Create new repository
                log.debug(f"Creating new repository: {metrics.path}")
                repo = Repository.from_metrics(metrics)
                # Set date_created for new records
                repo.date_created = time.time()
                session.add(repo)

            session.commit()
            # Return metrics object instead of Repository model
            return repo.to_metrics()
