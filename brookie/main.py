from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from brookie.api import sessions, trips

app = FastAPI(title="Brookie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(trips.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
