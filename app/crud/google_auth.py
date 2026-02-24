from sqlalchemy.orm import Session
from app.models import User

def get_user_by_email_or_google_id(db: Session, email: str, google_id: str):
    return db.query(User).filter(
        (User.email == email) | (User.google_id == google_id)
    ).first()


def create_google_user(db: Session, email: str, google_id: str, username: str):
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
    return user


def attach_google_id(db: Session, user: User, google_id: str):
    user.google_id = google_id
    db.commit()
    return user