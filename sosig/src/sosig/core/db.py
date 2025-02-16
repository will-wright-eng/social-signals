import os
import csv
import time
from typing import List, Optional, Generator
from contextlib import contextmanager

from sqlalchemy import func, text, inspect, create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import models
from .config import settings


class Database:
    """Database manager class handling all database operations"""

    _instance = None

    def __new__(cls, db_path: Optional[str] = None):
        """Implement proper singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection and session maker

        This will only run once due to singleton pattern
        """
        if hasattr(self, "engine"):  # Skip if already initialized
            return

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
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database schema and validate models"""
        # Check if tables exist before creating
        inspector = inspect(self.engine)
        if "repositories" not in inspector.get_table_names():
            models.Base.metadata.create_all(self.engine)
        models.Repository.validate_fields()  # Validate field consistency

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()  # noqa
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

    def remove_db(self, drop_db: bool = False) -> bool:
        """Remove a specific repository or drop the entire database.

        Args:
            drop_db: If True, drops the entire database file

        Returns:
            True if operation was successful, False otherwise
        """
        if drop_db:
            try:
                import os

                db_path = self.engine.url.database
                self.engine.dispose()  # Close all connections
                if os.path.exists(db_path):
                    os.remove(db_path)
                return True
            except Exception as e:
                raise Exception(f"Failed to drop database: {e}")

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

    def export_to_csv(self, output_dir: str = ".", fields: Optional[List[str]] = None) -> str:
        """Export repository data to a CSV file.

        Args:
            output_dir: Directory where the CSV file will be saved
            fields: List of field names to export. If None, exports all fields.

        Returns:
            Path to the created CSV file
        """
        repositories = self.get_all_repositories()

        if not repositories or len(repositories) == 0:
            raise Exception("No data to export")

        # Create filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"sosig_export_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        # Get all available field names from the first repository
        all_fields = [k for k, v in repositories[0].__dict__.items() if not k.startswith("_")]

        # Validate and filter fields if specified
        if fields:
            invalid_fields = [f for f in fields if f not in all_fields]
            if invalid_fields:
                raise ValueError(f"Invalid fields specified: {', '.join(invalid_fields)}")
            fieldnames = fields
        else:
            fieldnames = all_fields

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for repo in repositories:
                # Only write requested fields
                row = {k: v for k, v in repo.__dict__.items() if not k.startswith("_") and k in fieldnames}
                writer.writerow(row)

        return filepath


def get_db(db_path: Optional[str] = None) -> Database:
    """Get or create database instance singleton."""
    return Database(db_path)
