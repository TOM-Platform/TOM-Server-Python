from fastapi import APIRouter, HTTPException, Query
from Services.running_service.running_coach_repository import (
    get_sessions as repo_get_sessions,
    get_session_data as repo_get_session_data,
    get_available_weeks as repo_get_available_weeks,
    get_weekly_calories as repo_get_weekly_calories
)

running_coach_router = APIRouter(
    prefix="/running-coach",
    tags=["running-coach"]
)


@running_coach_router.get('/sessions')
def get_sessions(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    try:
        return repo_get_sessions(date)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@running_coach_router.get('/session-data')
def get_session_data(session_id: int = Query(..., description="Session ID")):
    try:
        return repo_get_session_data(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@running_coach_router.get('/available-weeks')
def get_available_weeks():
    try:
        return repo_get_available_weeks()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@running_coach_router.get('/weekly-calories')
def get_weekly_calories(week_start: int = Query(...), week_end: int = Query(...)):
    try:
        return repo_get_weekly_calories(week_start, week_end)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
