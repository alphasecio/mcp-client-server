# MCP Servers

[FastMCP](https://gofastmcp.com/getting-started/welcome) servers providing tools for some Google Cloud services. The servers will be available at `<URL>\mcp` upon deployment.

## Available Servers

### hello
- **Tools**: `greet`, `roll_dice`
- **Usage**: `python hello_server.py`

### scc
- **Tools**: `top_vulnerability_findings`, `get_finding_remediation`
- **Requirements**: Google Cloud credentials with SCC & CAI permissions
- **Usage**: `python scc_server.py`

### web-risk
- **Tools**: `lookup_url`
- **Requirements**: `GOOGLE_CLOUD_PROJECT` environment variable
- **Usage**: `python web_risk_server.py`

## Deployment

Each server includes a Dockerfile:
```bash
cd <server-name>
docker build -t <server-name>-mcp .
docker run -p 8000:8000 <server-name>-mcp
```

For production deployments, consider Google Cloud Run instead.
