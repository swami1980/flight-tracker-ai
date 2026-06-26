# Flight Tracker AI

An AI-powered flight tracker that answers natural language questions about flights currently on approach over Monroe Township, NJ (08831) heading to PHL, EWR, or JFK.

Built with FastAPI + Strands Agents (backend) and React + TypeScript (frontend).

---

## How it works

1. You ask a question like "What flights are overhead right now?"
2. The AI agent calls the OpenSky Network API to get live aircraft in the area
3. It cross-references each callsign against the OpenFlights route database to confirm origin and destination
4. It looks up the aircraft type and estimates ETA based on speed and distance
5. The answer streams back in real time — with a live tool call panel showing exactly what the agent did

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS, Vite |
| Backend | FastAPI, Strands Agents, Python 3.13 |
| AI | Claude Sonnet (Anthropic) |
| Flight data | OpenSky Network API (live) |
| Route data | OpenFlights routes.dat (static) |
| Aircraft data | OpenFlights planes.dat (static) |

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- An Anthropic API key

### 1. Download static data files

The data files are not committed to git (too large). Download them into `backend/app/data/`:

```bash
mkdir -p backend/app/data
curl -o backend/app/data/routes.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat
curl -o backend/app/data/planes.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/planes.dat
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Start the server:

```bash
uvicorn app.main:app --port 8001 --reload
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3001**

---

## Project structure

```
flight-tracker-ai/
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── flight_tools.py        # OpenSky + route + aircraft tools
│       │   └── flight_orchestrator.py # Strands agent + SSE streaming
│       ├── api/
│       │   └── flight_chat.py         # FastAPI SSE endpoint
│       ├── config.py
│       └── main.py
└── frontend/
    └── src/
        ├── api/client.ts              # SSE stream reader
        ├── hooks/useChat.ts           # React state management
        ├── components/
        │   ├── ChatWindow.tsx
        │   ├── Message.tsx
        │   └── ToolCallPanel.tsx      # Live agent reasoning panel
        └── App.tsx
```

---

## Coverage area

Bounding box centered on Monroe Township NJ (08831), ~25 mile radius.

Target airports and approach corridors:

| Airport | Heading range |
|---|---|
| PHL (Philadelphia) | 220° – 260° |
| EWR (Newark) | 340° – 020° |
| JFK (New York JFK) | 040° – 080° |
