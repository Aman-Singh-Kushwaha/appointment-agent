
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/chat")
def chat(request: ChatRequest):
    # Agent logic will be called here
    return {"response": f"You said: {request.message}"}
