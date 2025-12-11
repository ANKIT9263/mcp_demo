"""MCP Server with FastAPI wrapper"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import inspect
import sys
import os
from mcp.server.fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Create MCP server instance
mcp = FastMCP("Demo MCP Server")

# Define tools directly with decorators
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}! Welcome to the MCP server."

@mcp.tool()
def get_info() -> dict:
    """Get server information"""
    return {
        "server_name": "Demo MCP Server",
        "version": "1.0.0",
        "status": "running"
    }

@mcp.tool()
def get_config() -> str:
    """Get server configuration"""
    return "Server configuration: Demo mode enabled"

# Create FastAPI app
app = FastAPI(title="MCP Server")

# Request models
class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict = {}

# Health check
@app.get("/")
def root():
    return {"message": "MCP Server is running", "status": "ok"}

# Get available tools from MCP server
@app.get("/tools/list")
def list_tools():
    """List all available tools from MCP server"""
    tools_info = []

    # Get tools from MCP server
    for tool_name, tool_func in mcp._tool_manager._tools.items():
        # Get function metadata
        func = tool_func.fn
        sig = inspect.signature(func)

        params = {}
        required = []

        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == dict:
                param_type = "object"

            params[param_name] = {
                "type": param_type,
                "description": f"The {param_name} parameter"
            }
            required.append(param_name)

        tools_info.append({
            "name": tool_name,
            "description": func.__doc__ or f"Execute {tool_name}",
            "parameters": {
                "type": "object",
                "properties": params,
                "required": required
            }
        })

    return {"tools": tools_info}

# Execute a tool via MCP server
@app.post("/tools/execute")
def execute_tool(request: ToolCallRequest):
    """Execute a specific tool via MCP server"""
    # Get tool from MCP server
    if request.tool_name not in mcp._tool_manager._tools:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")

    try:
        tool = mcp._tool_manager._tools[request.tool_name]
        result = tool.fn(**request.arguments)
        return {"result": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8001)
