from fastapi import FastAPI, Depends, HTTPException, Query, Path, Body
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import traceback

from db import Base, engine, get_db
from run_schema import (
    CoachingRequest,
    CoachingResponse,
    CoachingUpdate,
    CoachingWithVoiceResponse,
    CoachingReportCreateRequest,
    CoachingReportResponse ,
)
from analysis_service import analyze_run
from llm_service import create_coaching_message
from tts_service import create_tts_file
from crud import (
    get_ai_coaching,
    get_ai_coachings,
    update_ai_coaching,
    delete_ai_coaching,
    create_ai_coaching_report,
    get_ai_coaching_report_by_activity_id,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RunSense AI Coaching Server",
    version="1.2.0",
    description="러닝 데이터와 족압 센서 데이터를 기반으로 AI 코칭 및 TTS 음성 응답을 제공하는 서버입니다.",
)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")


ERROR_RESPONSES = {
    400: {"description": "잘못된 요청 데이터"},
    404: {"description": "요청한 데이터를 찾을 수 없음"},
    422: {"description": "요청 Body 또는 파라미터 검증 실패"},
    500: {"description": "서버 내부 오류"},
}


def build_coaching_report(activity_id: int, db: Session):
    coachings = get_ai_coachings(db, activity_id=activity_id)

    if not coachings:
        raise HTTPException(
            status_code=404,
            detail="해당 러닝의 AI 코칭 기록이 없습니다.",
        )

    focus_count = {}

    for coaching in coachings:
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
        "activity_id": activity_id,
        "summary_title": "오늘의 분석",
        "total_coaching_count": len(coachings),
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
    summary="AI 러닝 코칭 생성",
    description="""
러닝 데이터와 족압 센서 데이터를 기반으로 AI 코칭을 생성합니다.

입력 데이터:
- pace: 페이스
- heart_rate: 심박수
- cadence: 케이던스
- foot_side: left 또는 right
- pronation_type: overpronation 또는 supination
- heel_strike_rate: 뒤꿈치 착지 비율
- hitmap_json: 5개 FSR 센서 데이터


처리 과정:
1. 러닝 데이터 분석
2. Gemini 기반 코칭 생성
3. TTS 음성 파일 생성
5. 코칭 결과 반환
""",
    responses={
        200: {
            "description": "실시간 AI 코칭 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "feedback_text": "호흡을 안정시키고 페이스를 낮춰보세요.",
                        "focus_point": "호흡 안정과 페이스 조절",
                        "rec_exercise": "가벼운 조깅과 호흡 조절 훈련",
                        "voice_file": "/audio/coach_xxxx.mp3",
                    }
                }
            },
        },
        422: {
            "description": "요청 Body 검증 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "int_parsing",
                                "loc": ["body", "heart_rate"],
                                "msg": "Input should be a valid integer",
                                "input": "높음",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
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
def create_coaching(data: CoachingRequest):
    try:
        analysis = analyze_run(data)
        feedback_text = create_coaching_message(data, analysis)
        voice_file = create_tts_file(feedback_text)

        return {
            "feedback_text": feedback_text,
            "focus_point": analysis["focus_point"],
            "rec_exercise": analysis["rec_exercise"],
            "voice_file": voice_file,
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="실시간 AI 코칭 생성 중 서버 오류가 발생했습니다.",
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
    summary="AI 코칭 요약 리포트 생성 및 저장",
    responses={
        200: {
            "description": "AI 코칭 리포트 생성 및 저장 성공",
            "content": {
                "application/json": {
                    "example": {
                        "report_id": 1,
                        "activity_id": 16,
                        "summary_title": "오늘의 분석",
                        "total_coaching_count": 13,
                        "items": [
                            {
                                "title": "호흡 안정과 페이스 조절",
                                "description": "호흡을 안정시키고 페이스를 낮춰보세요.",
                                "rec_exercise": "가벼운 조깅과 호흡 조절 훈련",
                                "count": 4,
                            }
                        ],
                    }
                }
            },
        },
        400: {
            "description": "리포트 저장 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "리포트 저장 중 DB 제약조건 오류가 발생했습니다."
                    }
                }
            },
        },
        404: {
            "description": "코칭 데이터 없음",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "해당 러닝의 AI 코칭 기록이 없습니다."
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
def create_coaching_report(
    data: CoachingReportCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        existing_report = get_ai_coaching_report_by_activity_id(
            db,
            data.activity_id,
        )

        if existing_report:
            return {
                "report_id": existing_report.report_id,
                "activity_id": existing_report.activity_id,
                "summary_title": existing_report.summary_title,
                "total_coaching_count": existing_report.total_coaching_count,
                "items": existing_report.items_json,
            }

        report_data = build_coaching_report(data.activity_id, db)

        report = create_ai_coaching_report(
            db=db,
            activity_id=report_data["activity_id"],
            summary_title=report_data["summary_title"],
            total_coaching_count=report_data["total_coaching_count"],
            items=report_data["items"],
        )

        return {
            "report_id": report.report_id,
            "activity_id": report.activity_id,
            "summary_title": report.summary_title,
            "total_coaching_count": report.total_coaching_count,
            "items": report.items_json,
        }

    except HTTPException:
        raise

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="리포트 저장 중 DB 제약조건 오류가 발생했습니다.",
        )

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 요약 리포트 생성 중 서버 오류가 발생했습니다.",
        )


@app.get(
    "/ai/coaching/report/{activity_id}",
    response_model=CoachingReportResponse,
    summary="저장된 AI 코칭 요약 리포트 조회",
    responses={
        200: {"description": "저장된 AI 코칭 리포트 조회 성공"},
        404: {
            "description": "저장된 리포트 없음",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "저장된 AI 코칭 리포트가 없습니다."
                    }
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "AI 코칭 요약 리포트 조회 중 서버 오류가 발생했습니다."
                    }
                }
            },
        },
    },
)
def read_coaching_report(
    activity_id: int = Path(
        ...,
        description="조회할 러닝 활동 ID",
        example=16,
    ),
    db: Session = Depends(get_db),
):
    try:
        report = get_ai_coaching_report_by_activity_id(db, activity_id)

        if report is None:
            raise HTTPException(
                status_code=404,
                detail="저장된 AI 코칭 리포트가 없습니다.",
            )

        return {
            "report_id": report.report_id,
            "activity_id": report.activity_id,
            "summary_title": report.summary_title,
            "total_coaching_count": report.total_coaching_count,
            "items": report.items_json,
        }

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 요약 리포트 조회 중 서버 오류가 발생했습니다.",
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