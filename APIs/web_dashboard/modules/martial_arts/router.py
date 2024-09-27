from fastapi import APIRouter, HTTPException, Request
from Services.martial_arts_service.martial_arts_repository import get_period_data, get_session_data_by_id

martial_arts_router = APIRouter(
    prefix="/martial-arts",
    tags=["martial-arts"]
)


@martial_arts_router.post("/")
async def get_period(request: Request):
    body = await request.json()
    start_date = body.get("start_date")
    end_date = body.get("end_date")

    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Invalid request")

    resp = get_period_data(start_date, end_date)
    return resp


@martial_arts_router.get("/{session_id}")
async def get_session(session_id: int):
    resp = get_session_data_by_id(session_id)
    return resp
