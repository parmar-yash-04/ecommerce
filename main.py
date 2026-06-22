from fastapi import FastAPI
from app.api.router import api_router
from app.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)