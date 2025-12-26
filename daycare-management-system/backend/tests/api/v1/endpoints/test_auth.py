# Authentication Endpoint Tests
# ============================================

import pytest
from fastapi import status
from app.core.config import settings


class TestUserRegistration:
    """Test user registration endpoint"""

    def test_register_new_user(self, client):
        """Test successful user registration"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "first_name": "New",
                "last_name": "User",
                "role": "staff"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert data["role"] == "staff"
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/register",
            json={
                "email": "test@example.com",  # Already exists
                "password": "password123",
                "first_name": "Duplicate",
                "last_name": "User",
                "role": "staff"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "first_name": "Test",
                "last_name": "User",
                "role": "staff"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoint"""

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, test_user, db):
        """Test login with inactive user account"""
        test_user.is_active = False
        db.commit()

        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in response.json()["detail"].lower()


class TestCurrentUser:
    """Test get current user endpoint"""

    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current authenticated user info"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert data["role"] == test_user.role

    def test_get_current_user_no_token(self, client):
        """Test getting current user without authentication fails"""
        response = client.get(f"{settings.API_V1_PREFIX}/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
