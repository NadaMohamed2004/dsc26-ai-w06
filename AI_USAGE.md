# AI usage

## Tools I used, and for what

I used Claude to write `retrieval.py`, `tools.py`, `server.py` and `agent.py` from the task
description, to test them, and to draft this file.

## Whether my assistant produced MCP v1 code, and how I noticed

It did not. `server.py` was written with `from mcp.server import MCPServer` and
`@server.tool()`; the task warns that the v1 `FastMCP` import fails under mcp 2.2.0. The code
was checked by running it with mcp 2.2.0 and calling the tools through the in-memory `Client`.

## One hostile model move I thought of that the spec does not mention

The model sends a tool name that is not a string, for example a list. A plain
`name in TOOLS` check would raise `TypeError` and crash the run. The loop checks the type
first, answers with one `unknown tool` error, and continues.
