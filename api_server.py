import logging
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
from config import config

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Quiz Bot API", version="1.0")


class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = "general"
    questions: Optional[List[dict]] = []


class QuizResponse(BaseModel):
    quiz_id: int
    title: str
    description: str
    category: str
    question_count: int


def verify_api_key(api_key: str = Header(None, alias="X-API-Key")):
    if api_key != config.API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0"}


@app.get("/api/stats")
async def get_stats(api_key: str = Header(None, alias="X-API-Key")):
    verify_api_key(api_key)
    return {
        "status": "ok",
        "message": "Stats endpoint - connect to database for real stats",
    }


@app.get("/api/quizzes/{quiz_id}")
async def get_quiz(
    quiz_id: int, api_key: str = Header(None, alias="X-API-Key")
):
    verify_api_key(api_key)
    return {
        "quiz_id": quiz_id,
        "message": "Quiz endpoint - connect to database for real data",
    }