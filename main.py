from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Chat API")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    response: str
    conversation_history: list
    tool_calls: list = []

# Health check endpoint
@app.get("/")
def root():
    return {"message": "Chat API is running", "status": "ok"}

# Single chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Process user message through LLM client and execute MCP tools
    Flow: Streamlit -> Chat API -> Client -> MCP Server -> Tools
    """
    try:
        from client import process_message
        result = process_message(request.message, request.conversation_history)
        return ChatResponse(
            response=result["response"],
            conversation_history=result["conversation_history"],
            tool_calls=result["tool_calls"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
