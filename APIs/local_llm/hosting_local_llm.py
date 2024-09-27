from typing import Optional, Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from .local_llm import generate_text, generate_text_with_history


class QuestionRequest(BaseModel):
    """
    Model for the request to generate an answer.
    """
    user_prompt: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.1


class QuestionRequestHistory(BaseModel):
    """
    Model for the request to generate an answer with history.
    """
    user_prompt: Optional[str] = None
    system_prompt: Optional[str] = None
    session_id: Optional[str] = None
    temperature: Optional[float] = 0.1


app = FastAPI()


@app.post("/generate-answer")
async def generate_answer(request_data: QuestionRequest):
    user_prompt = request_data.user_prompt
    system_prompt = request_data.system_prompt
    temperature = request_data.temperature

    if not user_prompt:
        raise HTTPException(status_code=400, detail="No question provided.")

    answer = generate_text(user_prompt, system_prompt, temperature)

    if answer == "No question provided.":
        raise HTTPException(status_code=400, detail=answer)

    return answer


history_store: Dict[str, List[dict]] = {}


@app.post("/generate-answer-history")
async def generate_answer_history(request_data: QuestionRequestHistory):
    user_prompt = request_data.user_prompt
    system_prompt = request_data.system_prompt
    session_id = request_data.session_id or "default_session"
    temperature = request_data.temperature

    if not user_prompt:
        raise HTTPException(status_code=400, detail="No question provided.")

    history = history_store.get(session_id, [])

    answer = generate_text_with_history(user_prompt, history, system_prompt, temperature)
    history_store[session_id] = history

    if answer == "No question provided.":
        raise HTTPException(status_code=400, detail=answer)

    return answer


if __name__ == "__main__":
    uvicorn.run("hosting_local_llm:app", host="0.0.0.0", port=5000, reload=True)
