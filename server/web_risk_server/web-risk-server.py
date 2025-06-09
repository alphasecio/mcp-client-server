import os, asyncio, logging
from typing import List, Dict, Any
from fastmcp import FastMCP
from google.cloud import webrisk_v1

mcp_server = FastMCP(name="WebRiskMCPServer")
logging.basicConfig(level=logging.INFO)

# Initialize Web Risk client using Application Default Credentials
_client = None

def _get_client():
    global _client
    if _client is None:
        try:
            # Client will automatically use Application Default Credentials
            _client = webrisk_v1.WebRiskServiceClient()
            logging.info("Web Risk client initialized with Application Default Credentials")
        except Exception as e:
            logging.error(f"Failed to initialize Web Risk client: {e}")
            raise
    return _client

def _get_threat_types() -> List[webrisk_v1.ThreatType]:
    return [
        webrisk_v1.ThreatType.MALWARE,
        webrisk_v1.ThreatType.SOCIAL_ENGINEERING,
        webrisk_v1.ThreatType.SOCIAL_ENGINEERING_EXTENDED_COVERAGE,
        webrisk_v1.ThreatType.UNWANTED_SOFTWARE
    ]

@mcp_server.tool()
def lookup_url(url: str) -> Dict[str, Any]:
    """Lookup a URL using Google Cloud Web Risk API"""
    logging.info(f"lookup_url() called with url={url}")

    if not url.strip():
        return {
            "error": "URL cannot be empty",
            "safe": None,
            "threats": []
        }

    try:
        client = _get_client()
        threat_types = _get_threat_types()
        
        # Call the Web Risk API to search for URL threats
        response = client.search_uris(
            uri=url,
            threat_types=threat_types
        )
        
        # Process the response
        if response.threat:
            threat_info = {
                "threat_types": [threat_type.name for threat_type in response.threat.threat_types],
                "expire_time": response.threat.expire_time.isoformat() if response.threat.expire_time else None
            }
            
            return {
                "safe": False,
                "url": url,
                "threat": threat_info,
                "message": f"URL {url} is associated with: {', '.join(threat_info['threat_types'])}"
            }
        else:
            return {
                "safe": True,
                "url": url,
                "threat": None,
                "message": f"URL {url} appears safe"
            }
            
    except Exception as e:
        logging.error(f"Error in lookup_url: {e}")
        return {
            "error": str(e),
            "safe": None,
            "url": url,
            "threat": None
        }

async def main():
  # Get port from environment variable
  port = int(os.environ.get("PORT", 8000))
  logging.info(f"Starting Web Risk MCP Server on port {port}...")  
  await mcp_server.run_async(transport="streamable-http", path="/mcp", host="0.0.0.0", port=port)

if __name__ == "__main__":
    asyncio.run(main())
