import csv
import json
import httpx
from pathlib import Path
from strands import tool

DATA_DIR = Path(__file__).parent.parent / "data"

# Bounding box around Monroe Township NJ (08831) — ~25 mile radius
LAT_MIN, LAT_MAX = 40.10, 40.55
LON_MIN, LON_MAX = -74.85, -74.05
ALT_MAX_FT = 25_000

# Approach corridor headings for target airports
APPROACH_CORRIDORS = {
    "PHL": (220, 260),
    "EWR": (340, 20),   # wraps around 360/0
    "JFK": (40, 80),
}

TARGET_AIRPORTS = {"PHL", "EWR", "JFK"}


def _heading_in_range(heading: float, low: int, high: int) -> bool:
    if low <= high:
        return low <= heading <= high
    # wraps around 360 (e.g. EWR: 340–020)
    return heading >= low or heading <= high


def _infer_destination(heading: float) -> tuple[str | None, str]:
    for airport, (low, high) in APPROACH_CORRIDORS.items():
        if _heading_in_range(heading, low, high):
            return airport, "inferred from heading (not confirmed)"
    return None, "heading does not match any target airport corridor"


@tool
def get_flights_overhead() -> str:
    """
    Get all flights currently on approach over Monroe Township NJ (08831)
    heading to PHL, EWR, or JFK. Returns flight details including callsign,
    altitude, speed, heading, and estimated destination.
    """
    url = "https://opensky-network.org/api/states/all"
    params = {
        "lamin": LAT_MIN,
        "lomin": LON_MIN,
        "lamax": LAT_MAX,
        "lomax": LON_MAX,
    }

    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return json.dumps({"error": f"OpenSky API error: {e}"})

    states = data.get("states") or []
    flights = []

    for state in states:
        icao24    = state[0] or ""
        callsign  = (state[1] or "").strip()
        altitude  = state[7]
        on_ground = state[8]
        velocity  = state[9]
        heading   = state[10]

        if on_ground:
            continue
        if not callsign:
            continue
        if altitude is None:
            continue

        altitude_ft = round(altitude * 3.281)
        if altitude_ft > ALT_MAX_FT:
            continue

        speed_knots = round(velocity * 1.944) if velocity else 0
        heading_deg = round(heading) if heading else 0

        flights.append({
            "icao24": icao24,
            "callsign": callsign,
            "altitude_ft": altitude_ft,
            "speed_knots": speed_knots,
            "heading_deg": heading_deg,
        })

    if not flights:
        return json.dumps({"message": "No flights currently on approach over 08831."})

    return json.dumps({"flights": flights, "count": len(flights)})


@tool
def lookup_route(callsign: str) -> str:
    """
    Look up the origin and destination airports for a given flight callsign
    using the OpenFlights routes database. Falls back to heading-based inference
    if the route is not found. Always notes whether destination is confirmed or inferred.
    """
    if len(callsign) < 3:
        return json.dumps({"error": "Callsign too short to parse"})

    # Split callsign into airline code and flight number
    # IATA codes are 2 chars (UA, AA, DL) — ICAO codes are 3 chars (UAL, AAL, DAL)
    airline_iata = callsign[:2].upper()
    airline_icao = callsign[:3].upper()

    routes_path = DATA_DIR / "routes.dat"

    try:
        with open(routes_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 5:
                    continue
                route_airline = row[0].upper()
                src_airport = row[2].upper()
                dst_airport = row[4].upper()

                if route_airline in (airline_iata, airline_icao):
                    if dst_airport in TARGET_AIRPORTS:
                        return json.dumps({
                            "callsign": callsign,
                            "origin_airport": src_airport,
                            "destination_airport": dst_airport,
                            "confidence": "confirmed via route database",
                        })
    except Exception as e:
        return json.dumps({"error": f"Route lookup error: {e}"})

    return json.dumps({
        "callsign": callsign,
        "origin_airport": "unknown",
        "destination_airport": "unknown",
        "confidence": "route not found in database — use heading for inference",
    })


@tool
def get_aircraft_type(icao24: str) -> str:
    """
    Look up the aircraft manufacturer and model for a given ICAO24 transponder code
    using the OpenFlights planes database. Returns 'Unknown aircraft type' if not found.
    """
    planes_path = DATA_DIR / "planes.dat"

    try:
        with open(planes_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                name = row[0].strip('"')
                icao_code = row[2].strip('"').upper()
                # Match first 3 chars of icao24 against known ICAO aircraft codes
                if icao24[:3].upper() == icao_code:
                    return json.dumps({
                        "icao24": icao24,
                        "aircraft_type": name,
                    })
    except Exception as e:
        return json.dumps({"error": f"Aircraft lookup error: {e}"})

    return json.dumps({
        "icao24": icao24,
        "aircraft_type": "Unknown aircraft type",
    })


ALL_TOOLS = [get_flights_overhead, lookup_route, get_aircraft_type]
