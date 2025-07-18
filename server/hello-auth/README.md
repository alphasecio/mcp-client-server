# Hello MCP Server with Auth

A minimal [FastMCP](https://github.com/jlowin/fastmcp) server with two sample tools and support for [bearer token authentication](https://gofastmcp.com/servers/auth/bearer) via OpenID Connect (OIDC). Ideal for quick experiments and testing with [MCP clients](https://github.com/alphasecio/mcp-client-server/blob/main/client/README.md). Can easily be deployed to serverless platforms like [Railway](https://railway.app/?referralCode=alphasec), [Cloud Run](https://cloud.google.com/run?hl=en), and others.

## 🛠️ Available Tools

| Tool          | Description                              |
|---------------|------------------------------------------|
| `request_info`| Returns info about the current request   |
| `roll_dice`   | Rolls n 6-sided dice                     |

## 🏁 Running the Server

* Set the following environment variables:
  * export `OIDC_ISSUER_URL`=`"https://your-issuer.com"`
  * export `OIDC_AUDIENCE`=`"your-audience"`
* Install the requirements: `pip install -r requirements.txt`
* Run the server: `python hello_server.py`
* The server starts at: `http://localhost:8000/mcp`

## 🔐 Authentication / Authorization
This server uses bearer token authentication based on OpenID Connect. Access tokens are validated using the issuer's JWKS endpoint: `{OIDC_ISSUER_URL}/.well-known/jwks.json`

If the token is missing or invalid, requests will be rejected with `401 Unauthorized`.
