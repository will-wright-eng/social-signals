from typing import List, Optional
from contextlib import contextmanager

from sqlalchemy import func, text, create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import models
from .config import settings


class Database:
    """Database manager class handling all database operations"""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection and session maker

        Args:
            db_path: Optional database URI. If not provided, uses the configured URI from settings.
        """
        self.engine = create_engine(db_path if db_path else settings.database.URI)
        self.SessionLocal = sessionmaker(bind=self.engine)
        models.Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def clear_all(self) -> int:
        """Clear all repositories from database.

        Returns:
            Number of repositories deleted
        """
        with self.get_session() as session:
            count = session.query(models.Repository).count()
            session.query(models.Repository).delete()
            return count

    def get_stats(self) -> dict:
        """Get database statistics.

        Returns:
            Dictionary containing database statistics
        """
        with self.get_session() as session:
            return {
                "total_repos": session.query(models.Repository).count(),
                "avg_signal": session.query(func.avg(models.Repository.social_signal)).scalar() or 0,
                "avg_stars": session.query(func.avg(models.Repository.stars)).scalar() or 0,
            }

    def remove_repository(self, repo_name: str) -> bool:
        """Remove a specific repository.

        Args:
            repo_name: Name of repository to remove

        Returns:
            True if repository was found and removed, False otherwise
        """
        with self.get_session() as session:
            repo = session.query(models.Repository).filter_by(name=repo_name).first()
            if repo:
                session.delete(repo)
                return True
            return False

    def optimize(self) -> None:
        """Optimize database by running VACUUM."""
        with self.get_session() as session:
            session.execute(text("VACUUM"))

    def get_repository(self, path: str) -> Optional[models.Repository]:
        """Get repository by path."""
        with self.get_session() as session:
            return session.query(models.Repository).filter_by(path=path).first()

    def get_all_repositories(self, sort_by: str = "social_signal") -> List[models.Repository]:
        """Get all repositories with optional sorting."""
        with self.get_session() as session:
            query = session.query(models.Repository)
            if hasattr(models.Repository, sort_by):
                query = query.order_by(getattr(models.Repository, sort_by).desc())
            return query.all()


# Global database instance
_db: Optional[Database] = None


def get_db(db_path: Optional[str] = None) -> Database:
    """Get or create database instance singleton."""
    global _db
    if _db is None:
        _db = Database(db_path)
    return _db


def init_db(db_path: Optional[str] = None) -> sessionmaker:
    """Initialize database and create tables (legacy support).

    Args:
        db_path: Optional database URI. If not provided, uses the configured URI from settings.
    """
    db = get_db(db_path)
    return db.SessionLocal
