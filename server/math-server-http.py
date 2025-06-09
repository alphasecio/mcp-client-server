import asyncio
from fastmcp import FastMCP

mcp_server = FastMCP(name="MathMCPServer")

@mcp_server.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers"""
    return a + b

@mcp_server.tool()
def multiply(a: int, b: int) -> int:
    """Multiplies two numbers"""
    return a * b

async def main():
    await mcp_server.run_async(transport="streamable-http", path="/mcp", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
