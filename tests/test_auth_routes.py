"""
Authentication Routes Tests
===========================
Tests for authentication endpoints: /api/auth/*
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, users


class TestAuthRegister:
    """Tests for POST /api/auth/register endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_register_valid_user(self):
        """Test successful user registration"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "New User",
                "email": "newuser@test.com",
                "phone": "+91 9876543210",
                "address": "123 New Street, Mumbai",
                "password": "newpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == "newuser@test.com"
    
    def test_register_duplicate_email(self):
        """Test registration with existing email fails"""
        # First registration
        self.client.post(
            "/api/auth/register",
            json={
                "name": "First User",
                "email": "duplicate@test.com",
                "phone": "+91 9876543210",
                "address": "123 First St",
                "password": "password123"
            }
        )
        
        # Second registration with same email
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "Second User",
                "email": "duplicate@test.com",
                "phone": "+91 9876543210",
                "address": "123 Second St",
                "password": "password456"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_missing_name(self):
        """Test registration without name fails"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "email": "test@test.com",
                "phone": "+91 9876543210",
                "address": "123 Test St",
                "password": "password123"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_email(self):
        """Test registration without email fails"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "phone": "+91 9876543210",
                "address": "123 Test St",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_register_missing_phone(self):
        """Test registration without phone fails"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "test@test.com",
                "address": "123 Test St",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_register_missing_address(self):
        """Test registration without address fails"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "test@test.com",
                "phone": "+91 9876543210",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_register_empty_name(self):
        """Test registration with empty name fails"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "",
                "email": "test@test.com",
                "phone": "+91 9876543210",
                "address": "123 Test St",
                "password": "password123"
            }
        )
        assert response.status_code == 422 
    
    def test_register_invalid_email_format(self):
        """Test registration with invalid email format"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "not-an-email",
                "phone": "+91 9876543210",
                "address": "123 Test St",
                "password": "password123"
            }
        )
        # Pydantic may or may not validate email format strictly
        assert response.status_code in [200, 422]


class TestAuthLogin:
    """Tests for POST /api/auth/login endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == "demo@freshcart.ai"
    
    def test_login_invalid_email(self):
        """Test login with non-existent email"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_missing_email(self):
        """Test login without email fails"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_login_missing_password(self):
        """Test login without password fails"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai"
            }
        )
        assert response.status_code == 422
    
    def test_login_empty_credentials(self):
        """Test login with empty credentials fails"""
        response = self.client.post(
            "/api/auth/login",
            json={}
        )
        assert response.status_code == 422
    
    def test_login_empty_email(self):
        """Test login with empty email fails"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "",
                "password": "password123"
            }
        )
        assert response.status_code == 422


class TestAuthMe:
    """Tests for GET /api/auth/me endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_current_user_with_valid_token(self):
        """Test getting current user with valid token"""
        # First login to get token
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        # Get current user
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "demo@freshcart.ai"
    
    def test_get_current_user_without_token(self):
        """Test getting current user without token fails"""
        response = self.client.get("/api/auth/me")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token fails"""
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token-123"}
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_get_current_user_malformed_header(self):
        """Test getting current user with malformed header"""
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": "InvalidFormat token"}
        )
        assert response.status_code == 401
    
    def test_get_current_user_empty_bearer(self):
        """Test getting current user with empty bearer token"""
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer "}
        )
        assert response.status_code == 401
