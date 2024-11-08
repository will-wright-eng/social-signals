from typing import List, Optional

from ..core.db import get_db
from ..core.models import Repository
from ..core.interfaces import RepoMetrics


class RepositoryDAO:
    """Data Access Object for Repository operations"""

    def __init__(self):
        self.db = get_db()

    def get_by_path(self, path: str) -> Optional[Repository]:
        """Get repository by path."""
        with self.db.get_session() as session:
            repo = session.query(Repository).filter_by(path=path).first()
            if repo:
                # Refresh to ensure all attributes are loaded
                session.refresh(repo)
                # Create a detached copy with all attributes loaded
                return Repository(
                    **{k: v for k, v in repo.__dict__.items() if not k.startswith("_")},
                )
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

    def save_metrics(self, metrics: RepoMetrics) -> Repository:
        """Save or update repository metrics."""
        with self.db.get_session() as session:
            existing = session.query(Repository).filter_by(path=metrics.path).first()

            if existing:
                # Update existing repository using from_metrics
                for field in RepoMetrics.get_metric_fields():
                    setattr(existing, field, getattr(metrics, field))
                repo = existing
            else:
                # Create new repository
                repo = Repository.from_metrics(metrics)
                session.add(repo)

            session.commit()
            # Create a detached copy with all attributes loaded
            return Repository(
                **{k: v for k, v in repo.__dict__.items() if not k.startswith("_")},
            )
