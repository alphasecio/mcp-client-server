import os
import asyncio
from fastmcp import Client
from fastmcp.client.auth import BearerAuth
from dotenv import load_dotenv

load_dotenv()

# Issued by Prefect Horizon for accessing MCP endpoint
FASTMCP_URL = os.getenv("FASTMCP_URL")
FASTMCP_API_KEY = os.getenv("FASTMCP_API_KEY")

async def main():
    async with Client(
        FASTMCP_URL,
        auth=BearerAuth(token=FASTMCP_API_KEY),
    ) as client:

        result = await client.call_tool("greet", {"name": "bob"})
        print(result.data)

asyncio.run(main())
