
from fastapi import FastAPI
from pydantic import BaseModel
from .app.agent import get_agent_response

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/chat")
def chat(request: ChatRequest):
    response = get_agent_response(request.message, request.session_id)
    return {"response": response}
