import os
from typing import Dict, Optional

from pydantic import Field, BaseModel


class LoggingConfig(BaseModel):
    DEBUG: bool = Field(default=False)
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )


class MetricsConfig(BaseModel):
    weights: Dict[str, float] = Field(
        default={
            "age": 0.2,
            "update_frequency": 0.3,
            "contributors": 0.2,
            "stars": 0.2,
            "commits": 0.1,
        },
    )
    normalizers: Dict[str, float] = Field(
        default={
            "max_age_days": 1825,  # 5 years
            "max_update_frequency_days": 30,
            "max_contributors": 50,
            "max_stars": 1000,
            "max_commits": 1000,
        },
    )


class DatabaseConfig(BaseModel):
    URI: str = Field(default="sqlite:///github_metrics.db")
    CACHE_TTL_HOURS: int = Field(default=24)


class APIConfig(BaseModel):
    OPENAI_MODEL: str = Field(default="gpt-4")
    OPENAI_API_KEY: str = Field(default=os.environ.get("OPENAI_API_KEY"))


class Config(BaseModel):
    """Main configuration class"""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    github_token: Optional[str] = Field(
        default=os.environ.get("GITHUB_TOKEN"),
        description="GitHub API token for extended rate limits",
    )


settings = Config()
