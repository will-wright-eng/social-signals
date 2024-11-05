import time

from sqlalchemy import Float, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

from .interfaces import RepoMetrics

Base = declarative_base()


class Repository(Base):
    __tablename__ = "repositories"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, unique=True, nullable=False)
    path: str = Column(String, nullable=False)
    age_days: float = Column(Float)
    update_frequency_days: float = Column(Float)
    contributor_count: int = Column(Integer)
    stars: int = Column(Integer)
    commit_count: int = Column(Integer)
    social_signal: float = Column(Float)
    last_analyzed: float = Column(Float, default=time.time)

    def __repr__(self) -> str:
        return f"Repository(name={self.name}, social_signal={self.social_signal})"

    def to_metrics(self) -> RepoMetrics:
        """Convert database model to RepoMetrics data class"""
        return RepoMetrics(
            name=self.name,
            path=self.path,
            age_days=self.age_days,
            update_frequency_days=self.update_frequency_days,
            contributor_count=self.contributor_count,
            stars=self.stars,
            commit_count=self.commit_count,
            social_signal=self.social_signal,
            last_analyzed=self.last_analyzed,
        )

    @classmethod
    def from_metrics(cls, metrics: RepoMetrics) -> "Repository":
        """Create database model from RepoMetrics data class"""
        return cls(
            name=metrics.name,
            path=metrics.path,
            age_days=metrics.age_days,
            update_frequency_days=metrics.update_frequency_days,
            contributor_count=metrics.contributor_count,
            stars=metrics.stars,
            commit_count=metrics.commit_count,
            social_signal=metrics.social_signal,
            last_analyzed=metrics.last_analyzed,
        )
