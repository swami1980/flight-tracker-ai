from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.flight_chat import router as flight_router

app = FastAPI(title="Flight Tracker AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flight_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
