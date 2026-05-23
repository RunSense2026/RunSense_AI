from sqlalchemy import Column, Integer, Float, String

from db import Base


class RunHistory(Base):

    __tablename__ = "run_history"

    id = Column(Integer, primary_key=True)

    user_id = Column(String)

    pace = Column(Float)
    heart_rate = Column(Integer)
    cadence = Column(Integer)