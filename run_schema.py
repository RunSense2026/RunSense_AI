from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class UserProfileContext(BaseModel):
    """
    백엔드가 마이페이지에서 조회해서
    AI 코칭 요청에 함께 전달하는 사용자 프로필입니다.

    FastAPI에서는 저장하지 않고
    AI 코칭 개인화에만 사용합니다.
    """

    age: Optional[int] = Field(
        None,
        ge=1,
        le=120,
        description="사용자 나이",
        examples=[24],
    )

    height: Optional[float] = Field(
        None,
        ge=100,
        le=250,
        description="사용자 키(cm)",
        examples=[170.0],
    )

    weight: Optional[float] = Field(
        None,
        ge=20,
        le=300,
        description="사용자 체중(kg)",
        examples=[70.0],
    )

    resting_heart_rate: Optional[int] = Field(
        None,
        ge=30,
        le=150,
        description="사용자 안정시 심박수(BPM)",
        examples=[58],
    )

    lthr: Optional[int] = Field(
        None,
        ge=30,
        le=250,
        description="가장 최근 LTHR 측정값(BPM)",
        examples=[162],
    )

class FootHitmap(BaseModel):
    forefoot_left: float = Field(..., example=20)
    forefoot_right: float = Field(..., example=15)
    midfoot_left: float = Field(..., example=10)
    midfoot_right: float = Field(..., example=8)
    heel: float = Field(..., example=70)


class FootData(BaseModel):
    pronation_type: Optional[str] = Field(None, example="overpronation")
    heel_strike_rate: Optional[float] = Field(None, example=85)
    hitmap: FootHitmap


class CoachingRequest(BaseModel):
    pace: float = Field(..., example=5.3)
    heart_rate: int = Field(..., example=180)
    cadence: int = Field(..., example=150)
    left_foot: FootData
    right_foot: FootData

    profile: Optional[UserProfileContext] = Field(
        None,
        description="마이페이지 프로필 기반 개인화 코칭 정보",
    )

class CoachingWithVoiceResponse(BaseModel):
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


class CoachingLogItem(BaseModel):
    feedback_text: str = Field(
        ...,
        example="왼발 압력을 줄이고 양발 균형을 맞춰보세요."
    )
    focus_point: Optional[str] = Field(
        None,
        example="왼발 하중 편중 개선"
    )
    rec_exercise: Optional[str] = Field(
        None,
        example="오른발 지지 안정화와 좌우 밸런스 훈련"
    )


class CoachingReportCreateRequest(BaseModel):
    coaching_logs: list[CoachingLogItem] = Field(
        ...,
        description="요약 리포트 생성에 사용할 AI 코칭 목록"
    )


class CoachingReportItem(BaseModel):
    title: str
    description: str
    rec_exercise: Optional[str] = None
    count: int


class CoachingReportResponse(BaseModel):
    summary_title: str
    total_coaching_count: int
    items: list[CoachingReportItem]