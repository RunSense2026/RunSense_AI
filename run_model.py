from sqlalchemy import Column, Integer, String, Text
from db import Base

class AICoaching(Base):
    __tablename__ = "ai_coaching"

    coaching_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    feedback_test = Column(Text, nullable=False)
    focus_point = Column(String, nullable=True)
    rec_exercise = Column(String, nullable=True)
