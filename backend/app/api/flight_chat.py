import json
import uuid
import asyncio
from queue import Queue, Empty
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.flight_orchestrator import run_agent, FlightEvent

router = APIRouter(prefix="/api/v1/flight", tags=["Flight"])


class ChatRequest(BaseModel):
    message: str


def _sse_event(event_type: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"


async def _stream_agent(message: str, session_id: str) -> AsyncGenerator[str, None]:
    event_queue: Queue = Queue()

    loop = asyncio.get_event_loop()
    agent_future = loop.run_in_executor(
        None,
        run_agent,
        message,
        event_queue,
    )

    yield _sse_event("session", {"session_id": session_id})
    yield _sse_event("status", {"message": "Checking flights overhead..."})

    while True:
        try:
            item = event_queue.get_nowait()
        except Empty:
            if agent_future.done():
                while True:
                    try:
                        item = event_queue.get_nowait()
                    except Empty:
                        break
                    if item is None:
                        break
                    yield _sse_event(item.event_type, item.payload)
                break
            await asyncio.sleep(0.05)
            continue

        if item is None:
            break

        yield _sse_event(item.event_type, item.payload)

    raw_answer = agent_future.result() if agent_future.done() else "No response."
    yield _sse_event("final_answer", {"content": raw_answer})
    yield _sse_event("done", {})


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    session_id = str(uuid.uuid4())
    return StreamingResponse(
        _stream_agent(req.message, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
