import os
import asyncio
from fastmcp import Client
from fastmcp.client.auth import BearerAuth
from dotenv import load_dotenv

load_dotenv()

FASTMCP_URL = os.getenv("FASTMCP_URL")
FASTMCP_API_KEY = os.getenv("FASTMCP_API_KEY")

async def main():
    async with Client(
        FASTMCP_URL,
        auth=BearerAuth(token=FASTMCP_API_KEY),
    ) as client:
        await client.ping()

        result = await client.call_tool("lookup_url", {"url": "https://testsafebrowsing.appspot.com/s/phishing.html"})
        print(result.data)

asyncio.run(main())
