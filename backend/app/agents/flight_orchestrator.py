import threading
from datetime import date
from queue import Queue

from strands import Agent
from strands.models.anthropic import AnthropicModel

from app.agents.flight_tools import ALL_TOOLS
from app.config import get_settings

_settings = get_settings()

SYSTEM_PROMPT = """You are a flight tracker assistant for a resident of Monroe Township, NJ (08831).

Today's date: {today}

You track flights currently on approach overhead heading to Philadelphia (PHL),
Newark (EWR), or JFK airports.

Workflow — follow this every time for a new flight question:
1. Call get_flights_overhead to get all aircraft currently in the area
2. For each flight returned, call lookup_route with its callsign to confirm destination
3. Call get_aircraft_type with its icao24 to identify the aircraft model
4. Filter to only flights whose destination is PHL, EWR, or JFK
5. Present a clear list with all details

For follow-up questions about a specific flight already retrieved:
- Reuse the data from the previous response — do NOT re-call the APIs
- Only call get_flights_overhead again if the user explicitly asks for a fresh update

Response format — for each flight include ALL of these:
- Callsign and aircraft type
- Origin airport (from lookup_route result — show IATA code and city if known, e.g. "ORD – Chicago O'Hare")
- Destination airport
- Altitude in feet
- Speed in knots
- ETA: estimate based on distance to airport and current speed
  (PHL is ~45 miles SW, EWR is ~35 miles NE, JFK is ~50 miles NE)
- Always state whether destination is confirmed via route database or inferred from heading
- If no flights found, say so clearly and suggest trying again in a few minutes

Be conversational but data-driven. Recruiters want facts, not hedging.
"""


class FlightEvent:
    def __init__(self, event_type: str, payload: dict):
        self.event_type = event_type
        self.payload = payload


def _make_model() -> AnthropicModel:
    return AnthropicModel(
        model_id="claude-sonnet-4-6",
        max_tokens=4096,
        client_args={"api_key": _settings.anthropic_api_key},
    )


def run_agent(user_message: str, event_queue: Queue) -> str:
    model = _make_model()
    prompt = SYSTEM_PROMPT.format(today=date.today().isoformat())
    result_holder = []

    class _Callback:
        def __call__(self, **kwargs):
            event_type = kwargs.get("event_type", "")
            data = kwargs.get("data", {})

            if event_type == "tool_use":
                event_queue.put(FlightEvent("tool_call", {
                    "tool_name": data.get("name", ""),
                    "tool_input": data.get("input", {}),
                }))
            elif event_type == "tool_result":
                raw = data.get("content", "")
                if isinstance(raw, list):
                    raw = str(raw)
                preview = raw[:1000] + "..." if len(raw) > 1000 else raw
                event_queue.put(FlightEvent("tool_result", {
                    "tool_name": data.get("tool_use_id", ""),
                    "result_preview": preview,
                }))

    def _run():
        try:
            agent = Agent(
                model=model,
                tools=ALL_TOOLS,
                system_prompt=prompt,
                callback_handler=_Callback(),
            )
            result = agent(user_message)
            result_holder.append(str(result))
        except Exception as e:
            result_holder.append(f"Agent error: {e}")
        finally:
            event_queue.put(None)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=120)

    return result_holder[0] if result_holder else "No response generated."
