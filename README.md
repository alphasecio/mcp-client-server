# MCP Client-Server

Model Context Protocol (MCP) client and server implementations using [FastMCP](https://gofastmcp.com/getting-started/welcome).

## Structure
```
├── client/      # MCP clients (Streamlit chatbot, Python examples)
├── server/      # MCP servers (hello, scc, web-risk)
└── README.md
```

## [Servers](server/README.md)

| Server     | Tools                                               | Description                           |
|------------|-----------------------------------------------------|---------------------------------------|
| hello      | greet, roll_dice                                    | Minimal example server                |
| scc        | top_vulnerability_findings, get_finding_remediation | Security Command Center integration   |
| web-risk   | lookup_url                                          | URL threat detection via Web Risk API |
