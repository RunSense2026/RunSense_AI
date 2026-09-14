from fastapi import FastAPI, Depends, HTTPException, Query, Path, Body
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from lthr_router import (
    router as lthr_router,
)
from profile_coaching_service import (
    analyze_profile_context,
)
import traceback

from db import Base, engine, get_db
from run_schema import (
    CoachingRequest,
    CoachingResponse,
    CoachingUpdate,
    CoachingWithVoiceResponse,
    CoachingReportCreateRequest,
    CoachingReportResponse,
)
from analysis_service import analyze_run
from llm_service import create_coaching_message
from tts_service import create_tts_file
from crud import (
    get_ai_coaching,
    get_ai_coachings,
    update_ai_coaching,
    delete_ai_coaching,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RunSense AI Coaching Server",
    version="1.2.0",
    description="러닝 데이터와 족압 센서 데이터를 기반으로 AI 코칭 및 TTS 음성 응답을 제공하는 서버입니다.",
)

app.include_router(
    lthr_router
)
app.mount("/audio", StaticFiles(directory="audio"), name="audio")


ERROR_RESPONSES = {
    400: {"description": "잘못된 요청 데이터"},
    404: {"description": "요청한 데이터를 찾을 수 없음"},
    422: {"description": "요청 Body 또는 파라미터 검증 실패"},
    500: {"description": "서버 내부 오류"},
}


def build_coaching_report(coaching_logs):
    if not coaching_logs:
        raise HTTPException(
            status_code=400,
            detail="요약 리포트를 생성할 AI 코칭 목록이 없습니다.",
        )

    focus_count = {}

    for coaching in coaching_logs:
        focus = coaching.focus_point or "기타 코칭"

        if focus not in focus_count:
            focus_count[focus] = {
                "count": 0,
                "feedback_text": coaching.feedback_text,
                "rec_exercise": coaching.rec_exercise,
            }

        focus_count[focus]["count"] += 1

    sorted_focus = sorted(
        focus_count.items(),
        key=lambda item: item[1]["count"],
        reverse=True,
    )

    items = []

    for focus, value in sorted_focus[:3]:
        items.append(
            {
                "title": focus,
                "description": value["feedback_text"],
                "rec_exercise": value["rec_exercise"],
                "count": value["count"],
            }
        )

    return {
        "summary_title": "오늘의 분석",
        "total_coaching_count": len(coaching_logs),
        "items": items,
    }


@app.get("/", summary="서버 기본 상태 확인")
def home():
    return {"message": "RunSense AI Coaching Server Running"}


@app.get("/health", summary="서버 헬스 체크")
def health():
    return {"status": "ok"}


@app.post(
    "/ai/coaching",
    response_model=CoachingWithVoiceResponse,
    summary="프로필 기반 AI 러닝 코칭 생성",
    description="""
현재 러닝 데이터, 양발 족압 센서 데이터,
사용자 프로필 정보를 기반으로 개인화 AI 코칭을 생성합니다.

### 러닝 데이터
- `pace`: 현재 페이스(초/km)
- `heart_rate`: 현재 심박수(BPM)
- `cadence`: 현재 케이던스(SPM)

### 족압 데이터
- `left_foot`: 왼발 분석 데이터
- `right_foot`: 오른발 분석 데이터
- `pronation_type`: 회내/회외 상태
- `heel_strike_rate`: 뒤꿈치 착지 비율
- `hitmap`: 5개 영역 족압 데이터

### 사용자 프로필
- `age`: 나이
- `height`: 키(cm)
- `weight`: 체중(kg)
- `resting_heart_rate`: 안정시 심박수(BPM)
- `lthr`: 최근 LTHR(BPM)

`profile` 및 프로필 내부 값은 선택값입니다.

LTHR가 존재하는 경우 현재 심박과 비교하여
Training Zone과 개인 심박 강도를 계산하고
AI 코칭에 반영합니다.

### 처리 과정
1. 러닝 및 족압 데이터 분석
2. 프로필 기반 심박 분석
3. Gemini/Groq 기반 AI 코칭 생성
4. TTS 음성 생성
5. 코칭 결과 반환

FastAPI에서는 사용자 프로필을 별도로 저장하지 않습니다.
""",
    responses={
        200: {
            "description": "AI 코칭 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "feedback_text": "심박이 높으니 페이스를 조금 낮춰보세요.",
                        "focus_point": "호흡 안정과 페이스 조절",
                        "rec_exercise": "가벼운 조깅과 호흡 조절 훈련",
                        "voice_file": "/audio/coach_xxxx.mp3",
                    }
                }
            },
        },

        400: {
            "description": "요청 값은 전달되었으나 서비스 로직상 처리할 수 없는 데이터",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "잘못된 러닝 데이터입니다."
                    }
                }
            },
        },

        422: {
            "description": "요청 Body의 타입, 필수 구조 또는 값 범위 검증 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "greater_than_equal",
                                "loc": [
                                    "body",
                                    "profile",
                                    "height"
                                ],
                                "msg": "Input should be greater than or equal to 100",
                                "input": 50
                            }
                        ]
                    }
                }
            },
        },

        500: {
            "description": "AI 코칭 생성 중 서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "실시간 AI 코칭 생성 중 서버 오류가 발생했습니다."
                    }
                }
            },
        },
    },
)
def create_coaching(
    data: CoachingRequest,
):

    try:

        analysis = analyze_run(
            data
        )



        profile_analysis = (
            analyze_profile_context(
                data
            )
        )


        analysis[
            "profile_context"
        ] = profile_analysis


        feedback_text = (
            create_coaching_message(
                data,
                analysis,
            )
        )


        voice_file = (
            create_tts_file(
                feedback_text
            )
        )


        return {
            "feedback_text":
                feedback_text,

            "focus_point":
                analysis[
                    "focus_point"
                ],

            "rec_exercise":
                analysis[
                    "rec_exercise"
                ],

            "voice_file":
                voice_file,
        }

    except Exception:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "실시간 AI 코칭 생성 중 "
                "서버 오류가 발생했습니다."
            ),
        )

@app.get(
    "/ai/coaching",
    response_model=list[CoachingResponse],
    summary="AI 코칭 목록 조회",
    description="activity_id를 입력하면 해당 러닝의 코칭만 조회하고, 입력하지 않으면 전체 코칭을 조회합니다.",
    responses={200: {"description": "AI 코칭 목록 조회 성공"}, **ERROR_RESPONSES},
)
def read_coachings(
    activity_id: int | None = Query(
        None,
        description="러닝 활동 ID",
        example=16,
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_ai_coachings(db, activity_id=activity_id)

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 목록 조회 중 서버 오류가 발생했습니다.",
        )


@app.post(
    "/ai/coaching/report",
    response_model=CoachingReportResponse,
    summary="AI 코칭 요약 리포트 생성",
    description="전달받은 AI 코칭 목록을 기반으로 요약 리포트를 생성합니다. 저장은 수행하지 않습니다.",
    responses={
        200: {
            "description": "AI 코칭 리포트 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "summary_title": "오늘의 분석",
                        "total_coaching_count": 4,
                        "items": [
                            {
                                "title": "왼발 하중 편중 개선",
                                "description": "왼발 압력을 줄이고 양발 균형을 맞춰보세요.",
                                "rec_exercise": "오른발 지지 안정화와 좌우 밸런스 훈련",
                                "count": 2,
                            },
                            {
                                "title": "케이던스 유지",
                                "description": "보폭을 줄이고 발걸음을 가볍게 해보세요.",
                                "rec_exercise": "짧은 보폭 러닝과 리듬 훈련",
                                "count": 1,
                            },
                        ],
                    }
                }
            },
        },
        400: {
            "description": "코칭 목록 없음",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "요약 리포트를 생성할 AI 코칭 목록이 없습니다."
                    }
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "AI 코칭 요약 리포트 생성 중 서버 오류가 발생했습니다."
                    }
                }
            },
        },
    },
)
def create_coaching_report(data: CoachingReportCreateRequest):
    try:
        report_data = build_coaching_report(
            coaching_logs=data.coaching_logs,
        )

        return report_data

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 요약 리포트 생성 중 서버 오류가 발생했습니다.",
        )


@app.get(
    "/ai/coaching/{coaching_id}",
    response_model=CoachingResponse,
    summary="AI 코칭 단건 조회",
    responses={200: {"description": "AI 코칭 단건 조회 성공"}, **ERROR_RESPONSES},
)
def read_coaching(
    coaching_id: int = Path(..., description="AI 코칭 ID", example=1),
    db: Session = Depends(get_db),
):
    try:
        coaching = get_ai_coaching(db, coaching_id)

        if coaching is None:
            raise HTTPException(
                status_code=404,
                detail="AI 코칭 기록을 찾을 수 없습니다.",
            )

        return coaching

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 조회 중 서버 오류가 발생했습니다.",
        )


@app.patch(
    "/ai/coaching/{coaching_id}",
    response_model=CoachingResponse,
    summary="AI 코칭 수정",
    responses={200: {"description": "AI 코칭 수정 성공"}, **ERROR_RESPONSES},
)
def update_coaching(
    coaching_id: int = Path(..., description="수정할 AI 코칭 ID", example=1),
    data: CoachingUpdate = Body(...),
    db: Session = Depends(get_db),
):
    try:
        coaching = get_ai_coaching(db, coaching_id)

        if coaching is None:
            raise HTTPException(
                status_code=404,
                detail="수정할 AI 코칭 기록을 찾을 수 없습니다.",
            )

        return update_ai_coaching(db, coaching, data)

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 수정 중 서버 오류가 발생했습니다.",
        )


@app.delete(
    "/ai/coaching/{coaching_id}",
    summary="AI 코칭 삭제",
    responses={200: {"description": "AI 코칭 삭제 성공"}, **ERROR_RESPONSES},
)
def delete_coaching(
    coaching_id: int = Path(..., description="삭제할 AI 코칭 ID", example=1),
    db: Session = Depends(get_db),
):
    try:
        coaching = get_ai_coaching(db, coaching_id)

        if coaching is None:
            raise HTTPException(
                status_code=404,
                detail="삭제할 AI 코칭 기록을 찾을 수 없습니다.",
            )

        delete_ai_coaching(db, coaching)

        return {
            "message": "AI 코칭 기록이 삭제되었습니다.",
            "coaching_id": coaching_id,
        }

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 삭제 중 서버 오류가 발생했습니다.",
        )