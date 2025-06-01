#!/usr/bin/env python3
"""Minimal MCP server for debugging"""

import asyncio
import sys
import logging
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Set up logging to stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Create server
server = Server("minimal-test")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    logger.info("Tools list requested")
    return [
        types.Tool(
            name="test_tool",
            description="A simple test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Test message"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    if name == "test_tool":
        message = arguments.get("message", "Hello World")
        return [
            types.TextContent(
                type="text",
                text=f"Test tool response: {message}"
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the server."""
    logger.info("Starting minimal MCP server...")
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Stdio server created, starting MCP server...")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="minimal-test",
                    server_version="1.0.0",
                    capabilities=types.ServerCapabilities(
                        tools=types.ToolsCapability(listChanged=False)
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1) 