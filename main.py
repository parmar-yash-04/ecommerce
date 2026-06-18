from fastapi import FastAPI
from app.api.router import api_router
from app.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ecommerce-frontend-snowy-two.vercel.app","http://localhost:5173","https://ecommerce-frontend-kkayklynr-yashs-projects-2f6e6ad4.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)