from fastapi import FastAPI
from sqlalchemy import text

from db import engine
from run_schema import RunData
from llm_service import create_message

from analysis_service import analyze_run
from prompt_service import build_prompt

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
    try:
        coaching_message = create_message(data)
        return {
            "message": coaching_message
        }
    except Exception as e:
        return {
            "error": str(e)
        }

@app.post("/runs")
def create_run(data: RunData):

    return {
        "message": "러닝 기록 저장 완료"
    }


@app.get("/runs")
def read_runs():

    return {
        "message": "전체 기록 조회"
    }