# AI usage

## Tools I used, and for what

I used Claude to develop `retrieval.py`, `tools.py`, `server.py`, and `agent.py` based on the task requirements. I also used it to test the implementation and prepare this document.

## Whether my assistant produced MCP v1 code, and how I noticed

No. The generated `server.py` used `from mcp.server import MCPServer` with the `@server.tool()` decorator, not the MCP v1 `FastMCP` import mentioned in the task warning, which does not work with mcp 2.2.0. To verify this, the code was run with mcp 2.2.0 and the tools were tested through the in-memory `Client`.

## One hostile model move I thought of that the spec does not mention

The model sends a tool name with an unexpected type, such as a list instead of a string. A direct check like `name in TOOLS` would raise a `TypeError` and stop the run. The loop checks the type first, returns an `unknown tool` error, and continues instead of crashing.
