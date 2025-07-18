import os, sys, random, asyncio, logging
from fastmcp import FastMCP, Context
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.dependencies import get_access_token, AccessToken

logging.basicConfig(level=logging.INFO)

try:
    OIDC_ISSUER_URL = os.getenv("OIDC_ISSUER_URL")
    OIDC_AUDIENCE = os.getenv("OIDC_AUDIENCE")

    if not OIDC_ISSUER_URL:
        raise ValueError("OIDC_ISSUER_URL environment variable not set.")
    if not OIDC_AUDIENCE:
        raise ValueError("OIDC_AUDIENCE environment variable not set.")

    auth = BearerAuthProvider(
        issuer=OIDC_ISSUER_URL,
        audience=OIDC_AUDIENCE,
        jwks_uri=f"{OIDC_ISSUER_URL}/.well-known/jwks.json",
        algorithm="RS256",
    )
    logging.info("BearerAuthProvider initialized.")
except Exception as e:
    logging.error(f"Error: {e}")
    exit(1)

try:
    mcp_server = FastMCP(
        name="HelloAuthMCPServer",
        auth=auth
    )
    logging.info("FastMCP server instance created.")
except Exception as e:
    logging.error(f"Failed to create FastMCP server instance: {e}")
    exit(1)

@mcp_server.tool()
async def request_info(ctx: Context) -> dict:
    """Return information about the current request."""
    logging.info(f"request_info() tool called")
    return {
        "session_id": ctx.session_id,
        "client_id": ctx.client_id or "Unknown client"
    }

@mcp_server.tool()
async def roll_dice(n_dice: int) -> list[int]:
    """Rolls n_dice 6-sided dice and returns the results."""
    logging.info(f"roll_dice() tool called with n_dice={n_dice}")
    return [random.randint(1, 6) for _ in range(n_dice)]

async def main():
    try:
        await mcp_server.run_async(
            transport="streamable-http", 
            path="/mcp", 
            host="0.0.0.0", 
            port=8000,
            log_level="info" 
        )
    except Exception as e:
        logging.error(f"FastMCP server failed to start: {e}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
