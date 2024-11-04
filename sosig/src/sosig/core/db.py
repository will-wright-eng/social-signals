from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .config import settings


def init_db(db_path: Optional[str] = None):
    """Initialize database and create tables

    Args:
        db_path: Optional database URI. If not provided, uses the configured URI from settings.
    """
    engine = create_engine(db_path if db_path else settings.database.URI)
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
