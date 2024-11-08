import os
import math
from typing import Dict, ClassVar
from pathlib import Path

from pydantic import Field, BaseModel
from rich.console import Console

console = Console()

PROJECT_NAME = "sosig"


class PathManager:
    """Manages XDG-compliant application paths"""

    @staticmethod
    def get_data_dir() -> Path:
        """Get XDG data directory for the application"""
        base_dir = (
            Path(os.environ.get("XDG_DATA_HOME", ""))
            if os.environ.get("XDG_DATA_HOME")
            else Path.home() / ".local" / "share"
        )
        data_dir = base_dir / PROJECT_NAME
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @staticmethod
    def get_config_dir() -> Path:
        """Get XDG config directory for the application"""
        base_dir = (
            Path(os.environ.get("XDG_CONFIG_HOME", ""))
            if os.environ.get("XDG_CONFIG_HOME")
            else Path.home() / ".config"
        )
        config_dir = base_dir / PROJECT_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir


class DatabaseConfig(BaseModel):
    """Database configuration settings"""

    filename: str = "github_metrics.db"
    CACHE_TTL_HOURS: int = Field(default=24)

    @property
    def URI(self) -> str:
        """Get SQLAlchemy connection string"""
        db_path = PathManager.get_data_dir() / self.filename
        return f"sqlite:///{db_path}"


class LoggingConfig(BaseModel):
    DEBUG: bool = Field(default=False)
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )


class MetricsConfig(BaseModel):
    """Configuration for repository metrics calculation"""

    DEFAULT_WEIGHTS: ClassVar[Dict[str, float]] = {
        "age": 0.15,
        "update_frequency": 0.25,
        "contributors": 0.15,
        "stars": 0.15,
        "commits": 0.1,
        "lines_of_code": 0.1,
        "open_issues": 0.1,
    }

    DEFAULT_NORMALIZERS: ClassVar[Dict[str, float]] = {
        "max_age_days": 1825,  # 5 years
        "max_update_frequency_days": 30,
        "max_contributors": 50,
        "max_stars": 1000,
        "max_commits": 1000,
        "max_lines_of_code": 1000000,
        "max_open_issues": 1000,
    }

    weights: Dict[str, float] = Field(
        default=DEFAULT_WEIGHTS,
        description="Weights for each metric in social signal calculation",
    )

    normalizers: Dict[str, float] = Field(
        default=DEFAULT_NORMALIZERS,
        description="Maximum values for normalizing each metric",
    )

    def validate_weights(self) -> None:
        """Ensure weights sum to 1.0"""
        if not math.isclose(sum(self.weights.values()), 1.0, rel_tol=1e-9):
            raise ValueError("Metric weights must sum to 1.0")


class Config(BaseModel):
    """Main configuration class"""

    PROJECT_NAME: str = PROJECT_NAME
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)


settings = Config()
