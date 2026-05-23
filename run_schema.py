from typing import Optional
from pydantic import BaseModel, Field

class CoachingRequest(BaseModel):
    activity_id: int = Field(..., description="러닝 활동 ID")
    user_id: int = Field(..., description="사용자 ID")
    pace: float = Field(..., description="페이스")
    heart_rate: int = Field(..., description="심박수")
    cadence: int = Field(..., description="케이던스")
    pronation_type: Optional[str] = Field(None, description="회내/회외 유형")
    heel_strike_rate: Optional[float] = Field(None, description="뒤꿈치 착지 비율")

class CoachingUpdate(BaseModel):
    feedback_test: Optional[str] = None
    focus_point: Optional[str] = None
    rec_exercise: Optional[str] = None

class CoachingResponse(BaseModel):
    coaching_id: int
    activity_id: int
    user_id: int
    feedback_test: str
    focus_point: Optional[str] = None
    rec_exercise: Optional[str] = None

    class Config:
        from_attributes = True
