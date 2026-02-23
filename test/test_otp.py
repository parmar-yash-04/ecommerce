import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import OTPVerification

def test_send_otp_success(client):
    otp_data = {
        "email": "test@example.com"
    }
    response = client.post("/otp/send", json=otp_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "OTP sent to your email"

def test_send_otp_invalid_email(client):
    otp_data = {
        "email": "invalidemail"
    }
    response = client.post("/otp/send", json=otp_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_send_otp_missing_email(client):
    response = client.post("/otp/send", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_send_multiple_otps(client, db_session):
    otp_data = {
        "email": "test@example.com"
    }
    response1 = client.post("/otp/send", json=otp_data)
    assert response1.status_code == status.HTTP_200_OK
    
    otp1 = db_session.query(OTPVerification).filter(
        OTPVerification.email == "test@example.com"
    ).order_by(OTPVerification.created_at.desc()).first()
    
    response2 = client.post("/otp/send", json=otp_data)
    assert response2.status_code == status.HTTP_200_OK
    
    otp2 = db_session.query(OTPVerification).filter(
        OTPVerification.email == "test@example.com"
    ).order_by(OTPVerification.created_at.desc()).first()
    
    assert otp1.otp_code != otp2.otp_code

def test_verify_otp_success(client, db_session):
    otp_data = {
        "email": "test@example.com"
    }
    client.post("/otp/send", json=otp_data)
    
    otp_record = db_session.query(OTPVerification).filter(
        OTPVerification.email == "test@example.com"
    ).order_by(OTPVerification.created_at.desc()).first()
    
    verify_data = {
        "email": "test@example.com",
        "otp": otp_record.otp_code
    }
    response = client.post("/otp/verify", json=verify_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "OTP verified"

def test_verify_otp_invalid_code(client):
    otp_data = {
        "email": "test@example.com"
    }
    client.post("/otp/send", json=otp_data)
    
    verify_data = {
        "email": "test@example.com",
        "otp": "000000"
    }
    response = client.post("/otp/verify", json=verify_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid OTP"

def test_verify_otp_wrong_email(client, db_session):
    otp_data = {
        "email": "test@example.com"
    }
    client.post("/otp/send", json=otp_data)
    
    otp_record = db_session.query(OTPVerification).filter(
        OTPVerification.email == "test@example.com"
    ).order_by(OTPVerification.created_at.desc()).first()
    
    verify_data = {
        "email": "wrong@example.com",
        "otp": otp_record.otp_code
    }
    response = client.post("/otp/verify", json=verify_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid OTP"

def test_verify_otp_expired(client, db_session):
    email = "test@example.com"
    otp_code = "123456"
    
    expired_otp = OTPVerification(
        email=email,
        otp_code=otp_code,
        expires_at=datetime.utcnow() - timedelta(minutes=10),
        is_used=False
    )
    db_session.add(expired_otp)
    db_session.commit()
    
    verify_data = {
        "email": email,
        "otp": otp_code
    }
    response = client.post("/otp/verify", json=verify_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "OTP expired"

def test_verify_otp_missing_email(client):
    verify_data = {
        "otp": "123456"
    }
    response = client.post("/otp/verify", json=verify_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_verify_otp_missing_code(client):
    verify_data = {
        "email": "test@example.com"
    }
    response = client.post("/otp/verify", json=verify_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_verify_otp_one_time_use(client, db_session):
    otp_data = {
        "email": "test@example.com"
    }
    client.post("/otp/send", json=otp_data)
    
    otp_record = db_session.query(OTPVerification).filter(
        OTPVerification.email == "test@example.com"
    ).order_by(OTPVerification.created_at.desc()).first()
    
    verify_data = {
        "email": "test@example.com",
        "otp": otp_record.otp_code
    }
    
    response1 = client.post("/otp/verify", json=verify_data)
    assert response1.status_code == status.HTTP_200_OK
    
    response2 = client.post("/otp/verify", json=verify_data)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert response2.json()["detail"] == "Invalid OTP"
