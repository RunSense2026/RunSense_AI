from fastapi import FastAPI, Depends, HTTPException, Query
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
)
from analysis_service import analyze_run
from llm_service import create_coaching_message
from tts_service import create_tts_file
from crud import (
    create_ai_coaching,
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

app.mount("/audio", StaticFiles(directory="audio"), name="audio")


ERROR_RESPONSES = {
    400: {
        "description": "잘못된 요청 데이터",
        "content": {
            "application/json": {
                "example": {
                    "detail": "요청 데이터가 올바르지 않습니다."
                }
            }
        },
    },
    404: {
        "description": "요청한 데이터를 찾을 수 없음",
        "content": {
            "application/json": {
                "example": {
                    "detail": "요청한 데이터를 찾을 수 없습니다."
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
                            "loc": ["body", "heart_rate"],
                            "msg": "Input should be a valid integer",
                            "type": "int_parsing",
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
                    "detail": "서버 내부 오류가 발생했습니다."
                }
            }
        },
    },
}


@app.get(
    "/",
    summary="서버 기본 상태 확인",
    description="RunSense AI Coaching Server가 실행 중인지 확인합니다.",
)
def home():
    return {"message": "RunSense AI Coaching Server Running"}


@app.get(
    "/health",
    summary="서버 헬스 체크",
    description="배포 환경에서 서버 상태를 확인하기 위한 헬스 체크 API입니다.",
)
def health():
    return {"status": "ok"}


@app.post(
    "/ai/coaching",
    response_model=CoachingWithVoiceResponse,
    summary="AI 러닝 코칭 생성",
    description="""
러닝 데이터와 족압 센서 데이터를 기반으로 AI 코칭을 생성합니다.

처리 과정:
1. 러닝 데이터 수신
2. 심박수, 케이던스, 족압 데이터 분석
3. Gemini 기반 코칭 문장 생성
4. TTS 음성 파일 생성
5. ai_coaching 테이블 저장
6. 코칭 결과 및 음성 파일 경로 반환

주의:
- activity_id는 running_activity 테이블에 존재하는 값이어야 합니다.
- hitmap_json은 5개 센서 규격을 사용합니다.
""",
    responses={
        200: {
            "description": "AI 코칭 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "coaching_id": 1,
                        "activity_id": 16,
                        "feedback_text": "호흡을 안정시키고 페이스를 낮춰보세요.",
                        "focus_point": "호흡 안정과 페이스 조절",
                        "rec_exercise": "가벼운 조깅과 호흡 조절 훈련",
                        "voice_file": "/audio/coach_xxxx.mp3",
                    }
                }
            },
        },
        **ERROR_RESPONSES,
    },
)
def create_coaching(data: CoachingRequest, db: Session = Depends(get_db)):
    try:
        analysis = analyze_run(data)
        feedback_text = create_coaching_message(data, analysis)
        voice_file = create_tts_file(feedback_text)

        coaching = create_ai_coaching(
            db=db,
            data=data,
            feedback_text=feedback_text,
            focus_point=analysis["focus_point"],
            rec_exercise=analysis["rec_exercise"],
        )

        return {
            "coaching_id": coaching.coaching_id,
            "activity_id": coaching.activity_id,
            "feedback_text": coaching.feedback_text,
            "focus_point": coaching.focus_point,
            "rec_exercise": coaching.rec_exercise,
            "voice_file": voice_file,
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="존재하지 않는 activity_id입니다. running_activity를 먼저 생성해주세요.",
        )

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="AI 코칭 생성 중 서버 오류가 발생했습니다.",
        )


@app.get(
    "/ai/coaching",
    response_model=list[CoachingResponse],
    summary="AI 코칭 목록 조회",
    description="activity_id를 기준으로 AI 코칭 목록을 조회합니다. activity_id가 없으면 전체 코칭 목록을 조회합니다.",
    responses={
        200: {
            "description": "AI 코칭 목록 조회 성공",
        },
        **ERROR_RESPONSES,
    },
)
def read_coachings(
    activity_id: int | None = Query(
        None,
        description="러닝 기록 ID. 입력 시 해당 러닝 기록에 연결된 AI 코칭만 조회합니다.",
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


@app.get(
    "/ai/coaching/{coaching_id}",
    response_model=CoachingResponse,
    summary="AI 코칭 단건 조회",
    description="coaching_id를 기준으로 AI 코칭 기록 1개를 조회합니다.",
    responses={
        200: {
            "description": "AI 코칭 단건 조회 성공",
        },
        **ERROR_RESPONSES,
    },
)
def read_coaching(coaching_id: int, db: Session = Depends(get_db)):
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
    description="coaching_id를 기준으로 AI 코칭 기록의 일부 값을 수정합니다.",
    responses={
        200: {
            "description": "AI 코칭 수정 성공",
        },
        **ERROR_RESPONSES,
    },
)
def update_coaching(
    coaching_id: int,
    data: CoachingUpdate,
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
    description="coaching_id를 기준으로 AI 코칭 기록을 삭제합니다.",
    responses={
        200: {
            "description": "AI 코칭 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "message": "AI 코칭 기록이 삭제되었습니다.",
                        "coaching_id": 1,
                    }
                }
            },
        },
        **ERROR_RESPONSES,
    },
)
def delete_coaching(coaching_id: int, db: Session = Depends(get_db)):
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