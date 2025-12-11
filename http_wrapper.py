from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Any, Dict

app = FastAPI(title="MCP Server HTTP Wrapper")

# Import tools from the MCP server
from mcp_server import add_numbers, greet, get_info, get_config

# Request models
class AddNumbersRequest(BaseModel):
    a: int
    b: int

class GreetRequest(BaseModel):
    name: str

# Health check endpoint
@app.get("/")
def root():
    return {"message": "MCP Server HTTP Wrapper is running", "status": "ok"}

# Tool endpoints
@app.post("/tools/add_numbers")
def tool_add_numbers(request: AddNumbersRequest):
    try:
        result = add_numbers(request.a, request.b)
        return {"result": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/greet")
def tool_greet(request: GreetRequest):
    try:
        result = greet(request.name)
        return {"result": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/get_info")
def tool_get_info():
    try:
        result = get_info()
        return {"result": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Resource endpoints
@app.get("/resources/config")
def resource_config():
    try:
        result = get_config()
        return {"result": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List all available tools
@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "add_numbers",
                "description": "Add two numbers together",
                "method": "POST",
                "endpoint": "/tools/add_numbers",
                "parameters": {"a": "int", "b": "int"}
            },
            {
                "name": "greet",
                "description": "Greet someone by name",
                "method": "POST",
                "endpoint": "/tools/greet",
                "parameters": {"name": "string"}
            },
            {
                "name": "get_info",
                "description": "Get server information",
                "method": "GET",
                "endpoint": "/tools/get_info",
                "parameters": {}
            }
        ],
        "resources": [
            {
                "name": "config",
                "description": "Get server configuration",
                "method": "GET",
                "endpoint": "/resources/config"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
