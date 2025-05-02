"""Tests for authentication routes."""

import pytest
from flask import url_for
from app.models.user import User


def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "password123"},
    )
    assert response.status_code == 201
    assert "user" in response.json
    assert response.json["user"]["username"] == "newuser"


def test_register_duplicate_username(client, test_user_id):
    """Test registration with existing username."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",  # Same as test_user
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert "error" in response.json


def test_login_success(client, test_user_id):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert "refresh_token" in response.json


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "wrongpass"},
    )
    assert response.status_code == 401
