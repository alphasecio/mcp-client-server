import asyncio
from fastmcp import FastMCP

mcp_server = FastMCP(name="HelloMCPServer")

@mcp_server.tool()
def greet(name: str) -> str:
    """Greets a user by name"""
    return f"Hello, {name}!"

async def main():
    await mcp_server.run_async(transport="streamable-http", path="/mcp", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
