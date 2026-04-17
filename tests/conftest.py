"""
Test Configuration and Shared Fixtures
=====================================
Shared pytest fixtures for FreshCart AI tests.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, users, products, orders, subscriptions, notifications, UserStore, ProductStore


@pytest.fixture(scope="function")
def client():
    """Create a test client for each test"""
    return TestClient(app)


@pytest.fixture(scope="function")
def fresh_stores():
    """Create fresh store instances for isolated testing"""
    user_store = UserStore()
    product_store = ProductStore()
    return {
        "users": user_store,
        "products": product_store,
    }


@pytest.fixture(scope="function")
def auth_headers():
    """Generate authorization headers with valid token"""
    from main import users
    result = users.authenticate("demo@freshcart.ai", "demo123")
    if result:
        return {"Authorization": f"Bearer {result['token']}"}
    return {}


@pytest.fixture(scope="function")
def demo_user_token():
    """Get demo user token"""
    from main import users
    result = users.authenticate("demo@freshcart.ai", "demo123")
    return result["token"] if result else None


@pytest.fixture(scope="function")
def sample_product():
    """Sample product data"""
    return {
        "id": 1,
        "name": "Organic Tomatoes",
        "category": "vegetables",
        "price": 3.99,
        "unit": "kg",
        "stock": 100,
        "description": "Farm fresh organic tomatoes"
    }


@pytest.fixture(scope="function")
def sample_cart_item():
    """Sample cart item data"""
    return {
        "product_id": 1,
        "name": "Organic Tomatoes",
        "price": 3.99,
        "quantity": 2,
        "subtotal": 7.98
    }


@pytest.fixture(scope="function")
def sample_order_items():
    """Sample order items"""
    return [
        {"product_id": 1, "name": "Organic Tomatoes", "price": 3.99, "quantity": 2, "subtotal": 7.98},
        {"product_id": 7, "name": "Red Apples", "price": 4.99, "quantity": 1, "subtotal": 4.99},
    ]


@pytest.fixture(scope="function")
def sample_address():
    """Sample delivery address"""
    return "123 Test Street, Mumbai, India"


@pytest.fixture
def mock_products():
    """Mock product catalog for testing"""
    return [
        {"id": 1, "name": "Organic Tomatoes", "category": "vegetables", "price": 3.99, "unit": "kg", "stock": 100},
        {"id": 2, "name": "Fresh Spinach", "category": "vegetables", "price": 2.49, "unit": "bunch", "stock": 80},
        {"id": 7, "name": "Red Apples", "category": "fruits", "price": 4.99, "unit": "kg", "stock": 200},
    ]
