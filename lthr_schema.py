from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


TEST_DURATION_SECONDS = 1800


# =========================================================
# 심박수 원본 데이터
# =========================================================

class HeartRateSample(BaseModel):
    elapsed_seconds: float = Field(
        ...,
        ge=0,
        le=TEST_DURATION_SECONDS,
        description=(
            "LTHR 테스트 시작 후 경과 시간(초). "
            "0=시작, 600=10분, 1800=30분"
        ),
        examples=[600.0],
    )

    heart_rate: int = Field(
        ...,
        ge=30,
        le=250,
        description="해당 시점에서 측정된 심박수(BPM)",
        examples=[158],
    )


# =========================================================
# LTHR 계산 요청
# =========================================================

class LTHRAnalyzeRequest(BaseModel):
    heart_rate_samples: list[HeartRateSample] = Field(
        ...,
        min_length=2,
        description="30분 동안 수집한 심박수 데이터",
    )

    previous_lthr: Optional[int] = Field(
        None,
        ge=30,
        le=250,
        description=(
            "이전 LTHR 측정값. "
            "최초 측정이면 null 또는 생략"
        ),
        examples=[158],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "heart_rate_samples": [
                    {
                        "elapsed_seconds": 0,
                        "heart_rate": 135,
                    },
                    {
                        "elapsed_seconds": 300,
                        "heart_rate": 145,
                    },
                    {
                        "elapsed_seconds": 600,
                        "heart_rate": 151,
                    },
                    {
                        "elapsed_seconds": 900,
                        "heart_rate": 157,
                    },
                    {
                        "elapsed_seconds": 1200,
                        "heart_rate": 160,
                    },
                    {
                        "elapsed_seconds": 1500,
                        "heart_rate": 163,
                    },
                    {
                        "elapsed_seconds": 1800,
                        "heart_rate": 165,
                    },
                ],
                "previous_lthr": 158,
            }
        }
    )


# =========================================================
# Training Zone
# =========================================================

class LTHRZoneResult(BaseModel):
    zone: str

    name: str

    min_bpm: Optional[int] = None

    max_bpm: Optional[int] = None

    duration_seconds: float

    percentage: float


# =========================================================
# LTHR 계산 응답
# =========================================================

class LTHRAnalyzeResponse(BaseModel):
    lthr: int

    previous_lthr: Optional[int] = None

    lthr_difference: Optional[int] = None

    max_heart_rate: int

    average_heart_rate: int

    zones: list[LTHRZoneResult]


# =========================================================
# LTHR AI 분석 요청
# =========================================================

class LTHRCoachingRequest(LTHRAnalyzeResponse):
    pass


# =========================================================
# LTHR AI 분석 응답
# =========================================================

class LTHRCoachingResponse(BaseModel):
    analysis: str