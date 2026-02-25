from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
import httpx
import json
import urllib.parse
from app.db.database import get_db
from app.core.oauth2 import create_access_token
from app.core.config import settings
from app.schemas import Token
from app.crud import google_auth as crud_google

router = APIRouter(prefix="/auth", tags=["Google Auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@router.get("/google")
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

@router.get("/google/callback")
def google_callback(code: str = Query(...), db: Session = Depends(get_db)):

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

    access_token = token_response.json().get("access_token")

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

    user = crud_google.get_user_by_email_or_google_id(db, email, google_id)

    if not user:
        user = crud_google.create_google_user(db, email, google_id, username)
    else:
        if not user.google_id:
            crud_google.attach_google_id(db, user, google_id)

    jwt_token = create_access_token(data={"user_id": user.user_id})

    user_data = {
        "email": user.email,
        "username": user.username,
        "user_id": user.user_id
    }

    encoded_user_data = urllib.parse.quote(json.dumps(user_data))
    
    redirect_url = (
        f"https://zealous-coast-001e51800.azurestaticapps.net/login?"
        f"access_token={jwt_token}&user_data={encoded_user_data}"
    )

    return RedirectResponse(url=redirect_url, status_code=302)

@router.post("/google/token", response_model=Token)
def google_token_exchange(code: str, db: Session = Depends(get_db)):
    # same logic as callback but return token only
    return {"access_token": "token_here", "token_type": "bearer"}