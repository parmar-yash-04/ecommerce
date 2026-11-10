from fastapi import FastAPI
from app.api.router import api_router
from app.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI()


def _allowed_origins(raw: str) -> list[str]:
    origins = []
    for candidate in raw.split(","):
        origin = candidate.strip().rstrip("/")
        if origin and origin not in origins:
            origins.append(origin)
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(settings.cors),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)