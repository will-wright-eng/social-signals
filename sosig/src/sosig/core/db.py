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
        self.engine = create_engine(
            db_path if db_path else settings.database.URI,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )
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
            repo = session.query(models.Repository).filter_by(path=path).first()
            if repo:
                # Load all relationships and attributes
                session.refresh(repo)
                # Create a detached copy with all attributes loaded
                detached_copy = models.Repository(
                    **{k: v for k, v in repo.__dict__.items() if not k.startswith("_")},
                )
                return detached_copy
            return None

    def get_all_repositories(self, sort_by: str = "social_signal") -> List[models.Repository]:
        """Get all repositories with optional sorting."""
        with self.get_session() as session:
            query = session.query(models.Repository)
            if hasattr(models.Repository, sort_by):
                query = query.order_by(getattr(models.Repository, sort_by).desc())

            # Load all results and create detached copies
            results = []
            for repo in query.all():
                session.refresh(repo)  # Ensure all attributes are loaded
                detached_copy = models.Repository(
                    **{k: v for k, v in repo.__dict__.items() if not k.startswith("_")},
                )
                results.append(detached_copy)

            return results

    def get_schema_info(self) -> dict:
        """Get database schema information.

        Returns:
            Dictionary containing tables, indexes, and triggers
        """
        with self.get_session() as session:
            # Get tables and their columns
            tables = {}
            for table in models.Base.metadata.tables.values():
                tables[table.name] = {
                    "columns": [
                        {
                            "name": col.name,
                            "type": str(col.type),
                            "nullable": col.nullable,
                            "primary_key": col.primary_key,
                        }
                        for col in table.columns
                    ],
                }

            # Get indexes and triggers using raw SQL (SQLite specific)
            indexes = session.execute(text("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")).fetchall()
            triggers = session.execute(text("SELECT name, tbl_name FROM sqlite_master WHERE type='trigger'")).fetchall()

            return {
                "tables": tables,
                "indexes": [{"name": idx[0], "table": idx[1]} for idx in indexes],
                "triggers": [{"name": trig[0], "table": trig[1]} for trig in triggers],
            }


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
    models.Repository.validate_fields()  # Validate field consistency
    return db.SessionLocal
