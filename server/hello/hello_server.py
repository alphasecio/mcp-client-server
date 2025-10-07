import random, asyncio, logging
from fastmcp import FastMCP

mcp = FastMCP(name="HelloMCPServer")

logging.basicConfig(level=logging.INFO)

@mcp.tool()
def greet(name: str) -> str:
    """Greets a user by name."""
    logging.info(f"greet() called with name={name}")
    return f"Hello, {name}!"

@mcp.tool()
def roll_dice(n_dice: int) -> list[int]:
    """Rolls n_dice 6-sided dice and returns the results."""
    logging.info(f"roll_dice() called with n_dice={n_dice}")
    return [random.randint(1, 6) for _ in range(n_dice)]

async def main():
    await mcp.run_async(transport="streamable-http", path="/mcp", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
