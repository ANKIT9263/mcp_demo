"""MCP Server Tools - Tool definitions only"""

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}! Welcome to the MCP server."

def get_info() -> dict:
    """Get server information"""
    return {
        "server_name": "Demo MCP Server",
        "version": "1.0.0",
        "status": "running"
    }

def get_config() -> str:
    """Get server configuration"""
    return "Server configuration: Demo mode enabled"
