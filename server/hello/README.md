# Hello MCP Server

A minimal [FastMCP](https://github.com/jlowin/fastmcp) server with two sample tools. Ideal for quick experiments and testing with [MCP clients](https://github.com/alphasecio/mcp-client-server/blob/main/client/README.md). Can easily be deployed to serverless platforms like [Railway](https://railway.app/?referralCode=alphasec), [Cloud Run](https://cloud.google.com/run?hl=en), and others.

## 🛠️ Available Tools

| Tool        | Description                  |
|-------------|------------------------------|
| `greet`     | Greets a user by name        |
| `roll_dice` | Rolls n 6-sided dice         |

## 🏁 Running the Server

* Install the requirements: `pip install -r requirements.txt`
* Run the server: `python hello_server.py`
* The server starts at: `http://localhost:8000/mcp`

## 🔐 Authentication / Authorization

Not implemented in this MCP server. See FastMCP [server authentication](https://gofastmcp.com/servers/auth/bearer) for details, and [hello-auth](https://github.com/alphasecio/mcp-client-server/tree/main/server/hello-auth) for a sample server.
