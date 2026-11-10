from fastapi import FastAPI
from app.api.router import api_router
from app.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_ORIGINS = (
    "http://localhost:5173",
    "https://ecommerce-frontend-snowy-two.vercel.app",
    "https://ecommerce-frontend-kkayklynr-yashs-projects-2f6e6ad4.vercel.app",
    "https://ecommercenexcart.netlify.app",
    "https://main--ecommercenexcart.netlify.app",
)


def _allowed_origins(raw: str) -> list[str]:
    origins = []
    for candidate in list(raw.split(",")) + list(BASE_ORIGINS):
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