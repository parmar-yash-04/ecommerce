import pytest
from fastapi import status

def test_login_success(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_email(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid Credentials"

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid Credentials"

def test_login_missing_username(client):
    response = client.post(
        "/auth/login",
        data={
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_missing_password(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_empty_credentials(client):
    response = client.post(
        "/auth/login",
        data={}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY