from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone_number: str
    password: str
    terms_accepted: bool = False

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    terms_accepted: bool
    phone_number: str
    is_verified: bool

    class Config:
        from_attributes = True