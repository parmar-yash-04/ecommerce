from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
import httpx
import json
import urllib.parse
from app.database import get_db
from app.models import User
from app.oauth2 import create_access_token
from app.schemas import Token
from app.config import settings

router = APIRouter(tags=["Google Auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@router.get("/auth/google")
def google_login():
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return {"authorization_url": url}

@router.get("/auth/google/callback")
def google_callback(code: str = Query(...), db: Session = Depends(get_db)):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    token_data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.google_redirect_uri
    }

    with httpx.Client() as client:
        token_response = client.post(GOOGLE_TOKEN_URL, data=token_data)
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    token_json = token_response.json()
    access_token = token_json.get("access_token")

    with httpx.Client() as client:
        userinfo_response = client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    userinfo = userinfo_response.json()
    google_id = userinfo.get("id")
    email = userinfo.get("email")
    username = userinfo.get("name")

    user = db.query(User).filter((User.email == email) | (User.google_id == google_id)).first()

    if not user:
        user = User(
            username=username or email.split("@")[0],
            email=email,
            google_id=google_id,
            hashed_password="google_oauth",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not user.google_id:
            user.google_id = google_id
            db.commit()

    jwt_token = create_access_token(data={"user_id": user.user_id})

    user_data = {
        "email": user.email,
        "username": user.username,
        "user_id": user.user_id
    }
    
    encoded_user_data = urllib.parse.quote(json.dumps(user_data))
    
    redirect_url = f"http://localhost:5173/login?access_token={jwt_token}&user_data={encoded_user_data}"
    return RedirectResponse(url=redirect_url)

@router.post("/auth/google/token", response_model=Token)
def google_token_exchange(code: str, db: Session = Depends(get_db)):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    token_data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.google_redirect_uri
    }

    with httpx.Client() as client:
        token_response = client.post(GOOGLE_TOKEN_URL, data=token_data)
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    token_json = token_response.json()
    access_token = token_json.get("access_token")

    with httpx.Client() as client:
        userinfo_response = client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    userinfo = userinfo_response.json()
    google_id = userinfo.get("id")
    email = userinfo.get("email")
    username = userinfo.get("name")

    user = db.query(User).filter((User.email == email) | (User.google_id == google_id)).first()

    if not user:
        user = User(
            username=username or email.split("@")[0],
            email=email,
            google_id=google_id,
            hashed_password="google_oauth",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not user.google_id:
            user.google_id = google_id
            db.commit()

    jwt_token = create_access_token(data={"user_id": user.user_id})

    return {"access_token": jwt_token, "token_type": "bearer"}