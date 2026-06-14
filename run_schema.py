from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CoachingRequest(BaseModel):
    pace: float = Field(..., description="페이스")
    heart_rate: int = Field(..., description="심박수")
    cadence: int = Field(..., description="케이던스")

    foot_side: Optional[str] = Field(None, description="발 방향 left/right")
    pronation_type: Optional[str] = Field(None, description="회내/회외 유형")
    heel_strike_rate: Optional[float] = Field(None, description="뒤꿈치 착지 비율")
    hitmap_json: Optional[Dict[str, Any]] = Field(None, description="족압 히트맵 데이터")


class CoachingWithVoiceResponse(BaseModel):
    coaching_id: int
    feedback_text: str
    focus_point: Optional[str] = None
    rec_exercise: Optional[str] = None
    voice_file: Optional[str] = None


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


class TTSResponse(BaseModel):
    text: str
    voice_file: str


class CoachingReportCreateRequest(BaseModel):
    activity_id: int = Field(
        ...,
        description="요약 리포트를 생성할 러닝 활동 ID",
        example=16,
    )


class CoachingReportItem(BaseModel):
    title: str
    description: str
    rec_exercise: str
    count: int


class CoachingReportResponse(BaseModel):
    report_id: Optional[int] = None
    activity_id: int
    summary_title: str
    total_coaching_count: int
    items: list[CoachingReportItem]

    class Config:
        from_attributes = True