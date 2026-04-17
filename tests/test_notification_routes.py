"""
Notification Routes Tests
========================
Tests for notification endpoints: /api/notifications/*
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, notifications


class TestGetNotifications:
    """Tests for GET /api/notifications endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_notifications_without_auth(self):
        """Test getting notifications without authentication"""
        response = self.client.get("/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # No user associated
    
    def test_get_notifications_with_auth(self):
        """Test getting notifications with authentication"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        response = self.client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestGetUnreadCount:
    """Tests for GET /api/notifications/unread-count endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_unread_count_without_auth(self):
        """Test getting unread count without auth"""
        response = self.client.get("/api/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] == 0
    
    def test_get_unread_count_with_auth(self):
        """Test getting unread count with auth"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        response = self.client.get(
            "/api/notifications/unread-count",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)


class TestMarkNotificationRead:
    """Tests for POST /api/notifications/{notification_id}/read endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_mark_read_without_auth(self):
        """Test marking notification as read without auth"""
        response = self.client.post("/api/notifications/1/read")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_mark_read_invalid_token(self):
        """Test marking notification with invalid token"""
        response = self.client.post(
            "/api/notifications/1/read",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
    
    def test_mark_read_nonexistent_notification(self):
        """Test marking non-existent notification as read"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        response = self.client.post(
            "/api/notifications/9999/read",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404


class TestMarkAllNotificationsRead:
    """Tests for POST /api/notifications/read-all endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_mark_all_read_without_auth(self):
        """Test marking all as read without auth"""
        response = self.client.post("/api/notifications/read-all")
        assert response.status_code == 401
    
    def test_mark_all_read_invalid_token(self):
        """Test marking all read with invalid token"""
        response = self.client.post(
            "/api/notifications/read-all",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
    
    def test_mark_all_read_with_valid_auth(self):
        """Test marking all read with valid auth"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        response = self.client.post(
            "/api/notifications/read-all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestDeleteNotification:
    """Tests for DELETE /api/notifications/{notification_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_delete_notification_without_auth(self):
        """Test deleting notification without auth"""
        response = self.client.delete("/api/notifications/1")
        assert response.status_code == 401
    
    def test_delete_notification_invalid_token(self):
        """Test deleting notification with invalid token"""
        response = self.client.delete(
            "/api/notifications/1",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
    
    def test_delete_nonexistent_notification(self):
        """Test deleting non-existent notification"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        response = self.client.delete(
            "/api/notifications/9999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
