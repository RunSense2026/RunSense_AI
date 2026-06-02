from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from run_schema import (
    CoachingRequest,
    CoachingResponse,
    CoachingUpdate,
    CoachingWithVoiceResponse,
    TTSResponse,
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
)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")


@app.get("/")
def home():
    return {"message": "RunSense AI Coaching Server Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    return {"database": "connected"}


@app.post("/tts/test", response_model=TTSResponse)
def tts_test(text: str):
    voice_file = create_tts_file(text)

    return {
        "text": text,
        "voice_file": voice_file,
    }


@app.post("/ai/test")
def ai_test(data: CoachingRequest):
    analysis = analyze_run(data)
    feedback_text = create_coaching_message(data, analysis)
    voice_file = create_tts_file(feedback_text)

    return {
        "issues": analysis["issues"],
        "feedback_text": feedback_text,
        "focus_point": analysis["focus_point"],
        "rec_exercise": analysis["rec_exercise"],
        "voice_file": voice_file,
    }


@app.post("/ai/coaching", response_model=CoachingWithVoiceResponse)
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/coaching", response_model=list[CoachingResponse])
def read_coachings(
    activity_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_ai_coachings(db, activity_id=activity_id)


@app.get("/ai/coaching/{coaching_id}", response_model=CoachingResponse)
def read_coaching(coaching_id: int, db: Session = Depends(get_db)):
    coaching = get_ai_coaching(db, coaching_id)

    if not coaching:
        raise HTTPException(status_code=404, detail="AI 코칭 기록을 찾을 수 없습니다.")

    return coaching


@app.patch("/ai/coaching/{coaching_id}", response_model=CoachingResponse)
def update_coaching(coaching_id: int, data: CoachingUpdate, db: Session = Depends(get_db)):
    coaching = get_ai_coaching(db, coaching_id)

    if not coaching:
        raise HTTPException(status_code=404, detail="수정할 AI 코칭 기록을 찾을 수 없습니다.")

    return update_ai_coaching(db, coaching, data)


@app.delete("/ai/coaching/{coaching_id}")
def delete_coaching(coaching_id: int, db: Session = Depends(get_db)):
    coaching = get_ai_coaching(db, coaching_id)

    if not coaching:
        raise HTTPException(status_code=404, detail="삭제할 AI 코칭 기록을 찾을 수 없습니다.")

    delete_ai_coaching(db, coaching)

    return {
        "message": "AI 코칭 기록이 삭제되었습니다.",
        "coaching_id": coaching_id,
    }