from fastapi import FastAPI
from sqlalchemy import text

from db import engine
from run_schema import RunData
from llm_service import create_message

from analysis_service import analyze_run
from prompt_service import build_prompt

from llm_service import create_coaching_message

from fastapi import HTTPException

app = FastAPI(
    title="RunSense AI Server",
    version="0.1.0"
)


@app.get("/")
def home():
    return {"message": "RunSense AI Server is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "connected"}


@app.post("/ai-test")
def ai_test(data: RunData):

    analysis = analyze_run(data)

    message = create_coaching_message(
        data,
        analysis
    )

    return {
        "status": analysis["status"],
        "issues": analysis["issues"],
        "message": message
    }

@app.post("/runs")
def create_run(data: RunData):
    try:
        analysis = analyze_run(data)

        message = create_coaching_message(
            data,
            analysis
        )

        return {
            "message": "러닝 기록 저장 완료",
            "status": analysis["status"],
            "issues": analysis["issues"],
            "coaching_message": message
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/runs")
def read_runs():

    return {
        "message": "전체 기록 조회"
    }