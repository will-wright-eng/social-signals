from sqlalchemy import Float, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

from .interfaces import RepoMetrics

Base = declarative_base()


class Repository(Base):
    __tablename__ = "repositories"

    # Define SQLAlchemy columns explicitly
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    username = Column(String, nullable=True)
    age_days = Column(Float, nullable=True)
    update_frequency_days = Column(Float, nullable=True)
    contributor_count = Column(Integer, nullable=True)
    stars = Column(Integer, nullable=True)
    commit_count = Column(Integer, nullable=True)
    social_signal = Column(Float, nullable=True)
    last_analyzed = Column(Float, nullable=True)
    lines_of_code = Column(Integer, nullable=True)
    open_issues = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"Repository(name={self.name}, social_signal={self.social_signal})"

    def to_metrics(self) -> RepoMetrics:
        """Convert database model to RepoMetrics data class"""
        return RepoMetrics(
            id=self.id,
            **{field: getattr(self, field) for field in RepoMetrics.get_metric_fields()},
        )

    @classmethod
    def from_metrics(cls, metrics: RepoMetrics) -> "Repository":
        """Create database model from RepoMetrics data class"""
        return cls(
            **{field: getattr(metrics, field) for field in RepoMetrics.get_metric_fields()},
        )

    @classmethod
    def validate_fields(cls):
        """Validate that Repository model matches RepoMetrics fields"""
        repo_fields = set(cls.__table__.columns.keys()) - {"id"}
        metrics_fields = set(RepoMetrics.get_metric_fields())

        if repo_fields != metrics_fields:
            missing = metrics_fields - repo_fields
            extra = repo_fields - metrics_fields
            raise ValueError(
                f"Repository model fields don't match RepoMetrics:\n"
                f"Missing fields: {missing}\n"
                f"Extra fields: {extra}",
            )
