import logging
import os
from collections.abc import AsyncIterator

from ag_ui.core import EventType, RunAgentInput, RunErrorEvent
from ag_ui.encoder import EventEncoder
from ag_ui_claude_sdk import ClaudeAgentAdapter
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

load_dotenv()

app = FastAPI(title="Claude Agent SDK Agent")
logger = logging.getLogger("claude_agent")

# Build the adapter once, at module scope. ClaudeAgentAdapter is a
# long-lived singleton that caches a worker (and its Claude SDK
# subprocess) per thread; constructing it per request would leak those
# workers and their subprocesses.
adapter = ClaudeAgentAdapter(
    name="claude_agent",
    options={
        "model": os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8"),
        "system_prompt": "You are a helpful assistant embedded in a CopilotKit app.",
        "tools": [],
        "permission_mode": "dontAsk",
        "max_turns": 10,
    },
)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/")
async def run_agent(input_data: RunAgentInput) -> StreamingResponse:
    encoder = EventEncoder()

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for event in adapter.run(input_data):
                yield encoder.encode(event)
        except Exception as error:
            # Agent and streaming failures become a graceful RUN_ERROR,
            # with the full detail logged server-side.
            logger.exception("Claude agent run failed")
            yield encoder.encode(
                RunErrorEvent(
                    type=EventType.RUN_ERROR,
                    message=str(error),
                )
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
