"""
[harness] NOT FROM THE DOCS — the app this repo serves
(`uv run uvicorn harness_app:app --reload --host 0.0.0.0 --port 8000`).
It is the Claude Agent SDK Quickstart's FastAPI `app` (main.py, verbatim and
unchanged, POST "/") plus one more endpoint, added at the user's request
(2026-11-17: "add weather tool as it's given" on Tool Rendering):

- Tool Rendering publishes src/app/demos/tool-rendering/weather_tool.snippet.py:
  an Anthropic tool schema (GET_WEATHER_TOOL) and its handler (get_weather),
  both complete. It is written verbatim by the doc generator and loaded here
  unchanged.
- The page's only way of attaching it is claude_agent_sdk_adapter.py, which
  needs seven names no page defines. So this module attaches the tool the way
  that excerpt does (an in-process MCP server in `mcp_servers`, the tool
  granted in `allowed_tools`), with harness-written glue in between: one SDK
  tool that passes the published schema through and returns the published
  handler's result as text, as the excerpt's `_make_sdk_tool` does.
- The agent is a second ClaudeAgentAdapter with the Quickstart's own options,
  plus that MCP server, served at POST /tool-rendering on the same app by an
  endpoint written like main.py's.

Tool name (fixed here, at the user's request): the model calls
`mcp__weather__get_weather`, and the adapter strips only its own
`mcp__ag_ui__` prefix, so AG-UI events would carry the prefixed name and the
page's per-tool `useRenderTool({ name: "get_weather" })` would never match.
The server can't be named `ag_ui` (the adapter replaces that key with its own
frontend-tool server). So the endpoint renames this server's tool calls back
to the published schema's name in TOOL_CALL_START and MESSAGES_SNAPSHOT
events; nothing else in the stream changes (README §9.2).
"""
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

import logging
from collections.abc import AsyncIterator

from ag_ui.core import BaseEvent, EventType, RunAgentInput, RunErrorEvent
from ag_ui.encoder import EventEncoder
from ag_ui_claude_sdk import ClaudeAgentAdapter
from claude_agent_sdk import create_sdk_mcp_server
from claude_agent_sdk import tool as sdk_tool
from fastapi.responses import StreamingResponse

from main import app

# ── The published file, loaded unchanged ────────────────────────────────────
_published = Path(__file__).parent / "src" / "app" / "demos" / "tool-rendering" / "weather_tool.snippet.py"
_spec = importlib.util.spec_from_file_location("weather_tool_snippet", _published)
weather_tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(weather_tool)
GET_WEATHER_TOOL = weather_tool.GET_WEATHER_TOOL
get_weather = weather_tool.get_weather


# ── [harness] glue: the published schema + handler as an SDK MCP tool ───────
@sdk_tool(GET_WEATHER_TOOL["name"], GET_WEATHER_TOOL["description"], GET_WEATHER_TOOL["input_schema"])
async def get_weather_sdk_tool(args: dict[str, Any]):
    return {"content": [{"type": "text", "text": json.dumps(get_weather(**args))}]}


WEATHER_MCP_SERVER = "weather"  # [harness] name chosen here; see the module docstring

# [harness] The Quickstart's adapter options (main.py), plus the weather tool.
tool_rendering_adapter = ClaudeAgentAdapter(
    name="claude_agent",
    options={
        "model": os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8"),
        "system_prompt": "You are a helpful assistant embedded in a CopilotKit app.",
        "tools": [],
        "permission_mode": "dontAsk",
        "max_turns": 10,
        "mcp_servers": {
            WEATHER_MCP_SERVER: create_sdk_mcp_server(WEATHER_MCP_SERVER, "1.0.0", tools=[get_weather_sdk_tool]),
        },
        "allowed_tools": [f"mcp__{WEATHER_MCP_SERVER}__{GET_WEATHER_TOOL['name']}"],
    },
)

# ── [harness] the tool's published name in AG-UI events ─────────────────────
_PREFIX = f"mcp__{WEATHER_MCP_SERVER}__"
logger = logging.getLogger("claude_agent.tool_rendering")


def _published_tool_names(event: BaseEvent) -> BaseEvent:
    """Drop this server's MCP prefix from tool-call names; leave all else as is."""
    if event.type == EventType.TOOL_CALL_START and event.tool_call_name.startswith(_PREFIX):
        return event.model_copy(update={"tool_call_name": event.tool_call_name.removeprefix(_PREFIX)})
    if event.type == EventType.MESSAGES_SNAPSHOT:
        messages = []
        for message in event.messages:
            calls = getattr(message, "tool_calls", None)
            if calls:
                message = message.model_copy(update={"tool_calls": [
                    call.model_copy(update={"function": call.function.model_copy(
                        update={"name": call.function.name.removeprefix(_PREFIX)})})
                    for call in calls
                ]})
            messages.append(message)
        return event.model_copy(update={"messages": messages})
    return event


@app.post("/tool-rendering")
async def run_tool_rendering_agent(input_data: RunAgentInput) -> StreamingResponse:
    """[harness] Same shape as main.py's run_agent, on the weather adapter."""
    encoder = EventEncoder()

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for event in tool_rendering_adapter.run(input_data):
                yield encoder.encode(_published_tool_names(event))
        except Exception as error:
            logger.exception("Tool Rendering agent run failed")
            yield encoder.encode(RunErrorEvent(type=EventType.RUN_ERROR, message=str(error)))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
