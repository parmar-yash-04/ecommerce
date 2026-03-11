from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class SyncRequest(BaseModel):
    force: bool = False