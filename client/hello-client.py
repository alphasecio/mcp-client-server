import os, asyncio
from fastmcp import Client

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://your-mcp-server.com/mcp")

async def main():
    async with Client(MCP_SERVER_URL, auth="oauth") as client:
        print("Authenticated successfully!")
    
        # Arguments are passed as a dictionary for the 'roll_dice' tool
        result = await client.call_tool("roll_dice", {"n_dice": 3})
        print(f"Rolled dice with results: {result.data}")

if __name__ == "__main__":
    asyncio.run(main())
