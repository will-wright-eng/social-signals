from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .config import settings


def init_db(db_path: str = None):
    """Initialize database and create tables

    Args:
        db_path: Optional database URI. If not provided, uses the configured URI from settings.
    """
    engine = create_engine(db_path or settings.database.URI)
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
