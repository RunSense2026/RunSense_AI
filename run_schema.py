from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CoachingRequest(BaseModel):
    activity_id: int = Field(..., description="러닝 활동 ID")

    pace: float = Field(..., description="페이스")
    heart_rate: int = Field(..., description="심박수")
    cadence: int = Field(..., description="케이던스")

    foot_side: Optional[str] = Field(None, description="발 방향 left/right")
    pronation_type: Optional[str] = Field(None, description="회내/회외 유형")
    heel_strike_rate: Optional[float] = Field(None, description="뒤꿈치 착지 비율")
    hitmap_json: Optional[Dict[str, Any]] = Field(None, description="족압 히트맵 데이터")


class CoachingUpdate(BaseModel):
    feedback_text: Optional[str] = None
    focus_point: Optional[str] = None
    rec_exercise: Optional[str] = None


class CoachingResponse(BaseModel):
    coaching_id: int
    activity_id: int
    feedback_text: str
    focus_point: Optional[str] = None
    rec_exercise: Optional[str] = None

    class Config:
        from_attributes = True


class CoachingWithVoiceResponse(BaseModel):
    coaching_id: int
    activity_id: int
    feedback_text: str
    focus_point: Optional[str] = None
    rec_exercise: Optional[str] = None
    voice_file: Optional[str] = None


class TTSResponse(BaseModel):
    text: str
    voice_file: str