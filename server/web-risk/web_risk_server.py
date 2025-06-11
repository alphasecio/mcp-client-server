import os, asyncio, logging
from typing import Dict, Any
from fastmcp import FastMCP
from google.cloud import webrisk_v1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp_server = FastMCP(name="WebRiskMCPServer")

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
if not project_id:
    raise EnvironmentError("GOOGLE_CLOUD_PROJECT environment variable is required but not set.")

# Initialize Web Risk client
_client = None

def _get_client():
    global _client
    if _client is None:
        try:
            _client = webrisk_v1.WebRiskServiceClient()
            logger.info("Web Risk client initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Web Risk client: {e}")
            raise
    return _client

@mcp_server.tool()
def lookup_url(url: str) -> Dict[str, Any]:
    """Lookup a URL using Google Cloud Web Risk API and check for threats."""
    logger.info(f"lookup_url() called with url={url}")

    if not url or not url.strip():
        return {
            "error": "URL cannot be empty",
            "safe": None
        }

    try:
        client = _get_client()
        
        # Define threat types to check
        threat_types = [
            webrisk_v1.ThreatType.MALWARE,
            webrisk_v1.ThreatType.SOCIAL_ENGINEERING,
            webrisk_v1.ThreatType.SOCIAL_ENGINEERING_EXTENDED_COVERAGE,
            webrisk_v1.ThreatType.UNWANTED_SOFTWARE
        ]

        # Call the Web Risk API to search for URL threats
        response = client.search_uris(
            uri=url.strip(),
            threat_types=threat_types
        )
        
        # Process the response
        if response.threat:
            threat_types_found = [t.name for t in response.threat.threat_types]
            return {
                "safe": False,
                "url": url,
                "threat_types": threat_types_found,
                "expire_time": response.threat.expire_time.isoformat() if response.threat.expire_time else None,
                "message": f"Threats found: {', '.join(threat_types_found)}"
            }
        else:
            return {
                "safe": True,
                "url": url,
                "message": f"No threats detection"
            }
            
    except Exception as e:
        logger.error(f"Error looking up URL: {e}")
        return {
            "error": str(e),
            "safe": None,
            "url": url
        }

async def main():
  port = int(os.environ.get("PORT", 8000))
  logger.info(f"Starting Web Risk MCP Server on port {port}...")  
  
  await mcp_server.run_async(transport="streamable-http", path="/mcp", host="0.0.0.0", port=port)

if __name__ == "__main__":
    asyncio.run(main())
