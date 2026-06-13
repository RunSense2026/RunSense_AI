from sqlalchemy import Column, Integer, String
from db import Base


class AICoaching(Base):
    __tablename__ = "ai_coaching"

    coaching_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, nullable=False)

    feedback_text = Column(String, nullable=False)
    focus_point = Column(String, nullable=True)
    rec_exercise = Column(String, nullable=True)

    from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from db import Base


class AICoachingReport(Base):
    __tablename__ = "ai_coaching_report"

    report_id = Column(Integer, primary_key=True, index=True)

    activity_id = Column(
        Integer,
        nullable=False,
        unique=True,
    )

    summary_title = Column(String, nullable=False)

    total_coaching_count = Column(Integer, nullable=False)

    items_json = Column(JSONB, nullable=False)