import json
from typing import Any, Dict, Optional
from pathlib import Path

from pydantic import Field, BaseModel
from rich.console import Console

from ..core.config import PROJECT_NAME
from ..core.logger import log

console = Console()


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
        description="Weights for different metrics in social signal calculation",
    )

    normalizers: Dict[str, float] = Field(
        default={
            "max_age_days": 1825,  # 5 years
            "max_update_frequency_days": 30,
            "max_contributors": 50,
            "max_stars": 1000,
            "max_commits": 1000,
        },
        description="Maximum values for metric normalization",
    )


class DatabaseConfig(BaseModel):
    """Configuration for database connection"""

    path: str = Field(
        default="sqlite:///github_metrics.db",
        description="Database connection string",
    )
    cache_ttl_hours: int = Field(
        default=24,
        description="Time-to-live for cached repository analysis in hours",
    )


class Config(BaseModel):
    """Main configuration class"""

    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub API token for extended rate limits",
    )


class ConfigManager:
    """Manages configuration file handling"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / PROJECT_NAME
        self.config_file = self.config_dir / "config.json"
        self.config: Config = self._load_config()

    def _create_default_config(self) -> Config:
        """Create default configuration"""
        return Config()

    def _load_config(self) -> Config:
        """Load configuration from file or create default"""
        try:
            if not self.config_dir.exists():
                self.config_dir.mkdir(parents=True)
                log.info(f"Created config directory: {self.config_dir}")

            if not self.config_file.exists():
                config = self._create_default_config()
                self.save_config(config)
                console.print(f"[green]Created new config file at: {self.config_file}[/green]")
                return config

            with open(self.config_file, "r") as f:
                config_data = json.load(f)
                return Config.model_validate(config_data)

        except Exception as e:
            log.error(f"Error loading config: {str(e)}")
            console.print("[yellow]Using default configuration due to error loading config file[/yellow]")
            return self._create_default_config()

    def save_config(self, config: Config) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config.model_dump(), f, indent=2)
            log.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            log.error(f"Error saving config: {str(e)}")
            raise

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        current_data = self.config.model_dump()

        def deep_update(d: dict, u: dict) -> dict:
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = deep_update(d[k], v)
                else:
                    d[k] = v
            return d

        updated_data = deep_update(current_data, updates)
        self.config = Config.model_validate(updated_data)
        self.save_config(self.config)

    def get_config(self) -> Config:
        """Get current configuration"""
        return self.config


config_manager = ConfigManager()
