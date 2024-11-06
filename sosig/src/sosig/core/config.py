import os
import math
from typing import Dict, Optional
from pathlib import Path

from pydantic import Field, BaseModel
from rich.console import Console

console = Console()

PROJECT_NAME = "sosig"


def get_data_dir() -> Path:
    """Get XDG data directory for the application"""
    xdg_data_home = os.environ.get("XDG_DATA_HOME", "")
    if xdg_data_home:
        base_dir = Path(xdg_data_home)
    else:
        base_dir = Path.home() / ".local" / "share"

    data_dir = base_dir / PROJECT_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_dir() -> Path:
    """Get XDG config directory for the application"""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "")
    if xdg_config_home:
        base_dir = Path(xdg_config_home)
    else:
        base_dir = Path.home() / ".config"

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
        db_path = get_data_dir() / self.filename
        return str(f"sqlite:///{db_path}")


class LoggingConfig(BaseModel):
    DEBUG: bool = Field(default=False)
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )


class MetricsConfig(BaseModel):
    """Configuration for repository metrics calculation"""

    weights: Dict[str, float] = Field(
        default={
            "age": 0.2,
            "update_frequency": 0.3,
            "contributors": 0.2,
            "stars": 0.2,
            "commits": 0.1,
        },
        description="Weights for each metric in social signal calculation",
    )

    normalizers: Dict[str, float] = Field(
        default={
            "max_age_days": 1825,  # 5 years
            "max_update_frequency_days": 30,
            "max_contributors": 50,
            "max_stars": 1000,
            "max_commits": 1000,
        },
        description="Maximum values for normalizing each metric",
    )

    def validate_weights(self) -> None:
        """Ensure weights sum to 1.0"""
        if not math.isclose(sum(self.weights.values()), 1.0, rel_tol=1e-9):
            raise ValueError("Metric weights must sum to 1.0")


class APIConfig(BaseModel):
    OPENAI_MODEL: str = Field(default="gpt-4")
    OPENAI_API_KEY: str = Field(default=os.environ.get("OPENAI_API_KEY"))


class Config(BaseModel):
    """Main configuration class"""

    PROJECT_NAME: str = PROJECT_NAME
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    github_token: Optional[str] = Field(
        default=os.environ.get("GITHUB_TOKEN"),
        description="GitHub API token for extended rate limits",
    )


settings = Config()
