import time

from sqlalchemy import Float, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    path = Column(String, nullable=False)
    age_days = Column(Float)
    update_frequency_days = Column(Float)
    contributor_count = Column(Integer)
    stars = Column(Integer)
    commit_count = Column(Integer)
    social_signal = Column(Float)
    last_analyzed = Column(Float, default=time.time)
