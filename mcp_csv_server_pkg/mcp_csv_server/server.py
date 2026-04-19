"""Low-level MCP server over stdio with natural-disaster CSV query tool."""

from __future__ import annotations

import asyncio
import traceback
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server

from mcp_csv_server.disasters import run_query_from_loaded

TOOL_NAME = "query_natural_disasters"

_TOOL_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "datasets": {
            "type": "string",
            "enum": ["1900", "1970", "both"],
            "description": 'Which extract to use: "1900" (1900-2021 file), "1970" (1970-2021 file), or "both".',
            "default": "both",
        },
        "year_min": {
            "type": "integer",
            "description": "Minimum Year (inclusive).",
        },
        "year_max": {
            "type": "integer",
            "description": "Maximum Year (inclusive).",
        },
        "country": {
            "type": "string",
            "description": "Case-insensitive substring match on Country.",
        },
        "iso": {
            "type": "string",
            "description": "Exact match on ISO country code (case-insensitive).",
        },
        "disaster_type": {
            "type": "string",
            "description": "Case-insensitive substring match on Disaster Type.",
        },
        "disaster_subgroup": {
            "type": "string",
            "description": "Case-insensitive substring match on Disaster Subgroup.",
        },
        "limit": {
            "type": "integer",
            "description": f"Max rows to return (default 50, hard cap 500).",
            "default": 50,
        },
        "columns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional subset of column names to return.",
        },
        "sort_by": {
            "type": "string",
            "description": "Column name to sort by before applying limit.",
        },
        "ascending": {
            "type": "boolean",
            "description": "Sort ascending (default true).",
            "default": True,
        },
        "max_chars": {
            "type": "integer",
            "description": "Maximum total characters in the text response (default 100000).",
        },
    },
}


def create_server() -> Server:
    server = Server(
        "mcp-csv-pandas",
        version="0.2.0",
        instructions=(
            "MCP server for EM-DAT-style natural disaster CSV data in this repository. "
            f"Use the tool {TOOL_NAME!r} to filter rows by Year, country, ISO, disaster type, "
            "and related fields. Data is loaded from dataset/csv (or MCP_DISASTER_CSV_DIR). "
            "Responses are plain text or compact markdown tables; row counts are capped."
        ),
    )

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=TOOL_NAME,
                description=(
                    "Query natural disaster records from bundled EM-DAT CSV exports using Pandas. "
                    "Filter by year range, country (substring), ISO code, disaster type/subgroup, "
                    "and choose which dataset file(s) to search (1900-2021, 1970-2021, or both)."
                ),
                inputSchema=_TOOL_INPUT_SCHEMA,
            )
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any] | None) -> types.CallToolResult:
        if name != TOOL_NAME:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool {name!r}. Available: {TOOL_NAME!r}.",
                    )
                ],
                isError=True,
            )
        try:
            text = run_query_from_loaded(arguments)
        except (ValueError, FileNotFoundError, OSError) as exc:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"{type(exc).__name__}: {exc}",
                    )
                ],
                isError=True,
            )
        except Exception:  # pragma: no cover - defensive
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unexpected error:\n{traceback.format_exc()}",
                    )
                ],
                isError=True,
            )
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=text)],
            isError=False,
        )

    return server


async def run_stdio() -> None:
    server = create_server()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )


def main() -> None:
    asyncio.run(run_stdio())
