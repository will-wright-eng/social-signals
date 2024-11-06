from .main import entry_point as cli  # noqa: F401
from .core.db import get_db

# Initialize database on application startup
db = get_db()
