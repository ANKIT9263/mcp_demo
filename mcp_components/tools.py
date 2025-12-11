"""MCP Server Tools - Tool definitions with decorators"""

from mcp_server import mcp

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

@mcp.resource("demo://config")
def get_config() -> str:
    """Get server configuration"""
    return "Server configuration: Demo mode enabled"
