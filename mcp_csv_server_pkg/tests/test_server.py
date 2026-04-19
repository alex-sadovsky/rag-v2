"""Tests for MCP server wiring and disaster query tool."""

import mcp.types as types
import pytest

from mcp_csv_server.server import TOOL_NAME, create_server


@pytest.mark.asyncio
async def test_list_tools_includes_query_natural_disasters() -> None:
    server = create_server()
    handler = server.request_handlers[types.ListToolsRequest]
    result = await handler(None)
    inner = result.root
    assert isinstance(inner, types.ListToolsResult)
    assert len(inner.tools) == 1
    assert inner.tools[0].name == TOOL_NAME
    assert inner.tools[0].inputSchema.get("type") == "object"


@pytest.mark.asyncio
async def test_call_tool_unknown_name_errors() -> None:
    server = create_server()
    handler = server.request_handlers[types.CallToolRequest]
    req = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(name="nope", arguments={}),
    )
    result = await handler(req)
    inner = result.root
    assert isinstance(inner, types.CallToolResult)
    assert inner.isError is True


@pytest.mark.asyncio
async def test_call_tool_validation_error_on_bad_datasets() -> None:
    server = create_server()
    handler = server.request_handlers[types.CallToolRequest]
    req = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name=TOOL_NAME,
            arguments={"datasets": "invalid"},
        ),
    )
    result = await handler(req)
    inner = result.root
    assert isinstance(inner, types.CallToolResult)
    assert inner.isError is True
