"""MCP server exposing the Hisn triage tools."""

from typing import Any

from mcp.server import MCPServer

from hisn import retrieval, tools

server = MCPServer("hisn-triage")


@server.tool()
def lookup_asset(host: str) -> dict[str, Any]:
    """Look up a host's owner, criticality and environment."""
    return tools.lookup_asset(host)


@server.tool()
def search_runbooks(query: str, k: int = 3) -> list[dict[str, Any]]:
    """Search the incident runbooks and return the best matches."""
    return retrieval.search_runbooks(query, k)


@server.tool()
def related_alerts(rule_id: str, agent: str, around: str, window_minutes: int = 60) -> dict[str, Any]:
    """Count alerts with the same rule and agent in the minutes before a time."""
    return tools.related_alerts(rule_id, agent, around, window_minutes)


if __name__ == "__main__":
    server.run()
