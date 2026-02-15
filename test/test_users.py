import pytest
from fastapi import status

def test_create_user_success(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "phone_number": "5551234567",
        "password": "password123"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["phone_number"] == user_data["phone_number"]
    assert "user_id" in data
    assert "hashed_password" not in data

def test_create_user_duplicate_email(client, test_user):
    user_data = {
        "username": "anotheruser",
        "email": "test@example.com",
        "phone_number": "5551234567",
        "password": "password123"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already exists"

def test_create_user_invalid_email(client):
    user_data = {
        "username": "newuser",
        "email": "invalidemail",
        "phone_number": "5551234567",
        "password": "password123"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_user_missing_username(client):
    user_data = {
        "email": "newuser@example.com",
        "phone_number": "5551234567",
        "password": "password123"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_user_missing_email(client):
    user_data = {
        "username": "newuser",
        "phone_number": "5551234567",
        "password": "password123"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_user_missing_phone(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_user_missing_password(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "phone_number": "5551234567"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_users_endpoint_success(client, test_user):
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = client.post("/users/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_users_endpoint_wrong_email(client):
    login_data = {
        "email": "wrong@example.com",
        "password": "testpass123"
    }
    response = client.post("/users/login", json=login_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid Credentials"

def test_login_users_endpoint_wrong_password(client, test_user):
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/users/login", json=login_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid Credentials"
