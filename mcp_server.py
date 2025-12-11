from mcp.server.fastmcp import FastMCP
from tools import add_numbers, greet, get_info, get_config

# Create an MCP server
mcp = FastMCP("Demo MCP Server")

# Register tools using decorators
mcp.tool()(add_numbers)
mcp.tool()(greet)
mcp.tool()(get_info)

# Register resource
mcp.resource("demo://config")(get_config)

if __name__ == "__main__":
    mcp.run()
