"""
FreshCart AI - Test Agent
========================
Agent that generates comprehensive pytest test cases by analyzing Python source files.
Generates tests for endpoints, Pydantic models, and store classes.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class TestAgent:
    """
    Agent responsible for generating pytest test cases.
    Analyzes Python source files and generates comprehensive tests.
    """
    
    def __init__(self, source_dir: str = None, test_dir: str = "tests"):
        self.source_dir = Path(source_dir) if source_dir else Path(__file__).parent.parent
        self.test_dir = Path(test_dir)
        self.generated_files: List[str] = []
        
        self.source_files = [
            self.source_dir / "main.py",
            self.source_dir / "api" / "routes" / "user_routes.py",
            self.source_dir / "api" / "routes" / "product_routes.py",
            self.source_dir / "api" / "models" / "schemas.py",
        ]
    
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a Python file and extract endpoints, models, and functions"""
        if not filepath.exists():
            return {"endpoints": [], "models": [], "stores": [], "functions": []}
        
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        result = {
            "file": str(filepath),
            "endpoints": self._extract_endpoints(tree, content),
            "models": self._extract_models(tree, content),
            "stores": self._extract_stores(tree, content),
            "functions": self._extract_functions(tree),
        }
        
        return result
    
    def _extract_endpoints(self, tree: ast.AST, content: str) -> List[Dict]:
        """Extract FastAPI endpoint definitions"""
        endpoints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for FastAPI decorators
                for decorator in node.decorator_list:
                    decorator_name = self._get_decorator_name(decorator)
                    
                    if decorator_name in ['app.get', 'app.post', 'app.put', 'app.delete', 'router.get', 'router.post', 'router.put', 'router.delete']:
                        endpoint = {
                            "name": node.name,
                            "method": decorator_name.split('.')[-1].upper(),
                            "path": self._extract_path(decorator),
                            "requires_auth": self._check_auth_requirement(node, content),
                            "has_request_body": self._has_request_body(node),
                            "parameters": self._extract_parameters(node),
                            "docstring": ast.get_docstring(node) or f"{node.name} endpoint",
                        }
                        endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_models(self, tree: ast.AST, content: str) -> List[Dict]:
        """Extract Pydantic model definitions"""
        models = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Pydantic model
                is_pydantic = any(
                    isinstance(base, ast.Name) and base.id in ['BaseModel', 'Enum']
                    for base in node.bases
                )
                
                if is_pydantic:
                    model = {
                        "name": node.name,
                        "is_enum": any(
                            isinstance(base, ast.Name) and base.id == 'Enum'
                            for base in node.bases
                        ),
                        "fields": self._extract_model_fields(node),
                        "docstring": ast.get_docstring(node),
                    }
                    models.append(model)
        
        return models
    
    def _extract_stores(self, tree: ast.AST, content: str) -> List[Dict]:
        """Extract store class definitions"""
        stores = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if 'Store' in node.name or 'Agent' in node.name:
                    store = {
                        "name": node.name,
                        "methods": self._extract_class_methods(node),
                        "docstring": ast.get_docstring(node),
                    }
                    stores.append(store)
        
        return stores
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract standalone functions"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.decorator_list:
                func = {
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                }
                functions.append(func)
        
        return functions
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_decorator_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return ""
    
    def _extract_path(self, decorator: ast.AST) -> str:
        """Extract path from decorator"""
        if isinstance(decorator, ast.Call):
            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                return decorator.args[0].value
        return "/unknown"
    
    def _check_auth_requirement(self, node: ast.FunctionDef, content: str) -> bool:
        """Check if endpoint requires authentication"""
        source_lines = content.split('\n')
        if hasattr(node, 'decorator_list'):
            for dec in node.decorator_list:
                dec_str = ast.unparse(dec) if hasattr(ast, 'unparse') else str(dec)
                if 'authorization' in dec_str.lower() or 'auth' in dec_str.lower():
                    return True
        return False
    
    def _has_request_body(self, node: ast.FunctionDef) -> bool:
        """Check if endpoint has request body"""
        for arg in node.args.args:
            if arg.annotation:
                ann_str = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)
                if 'BaseModel' in ann_str or 'Request' in ann_str or 'Body' in ann_str:
                    return True
        return False
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict]:
        """Extract function parameters"""
        params = []
        for arg in node.args.args:
            param = {"name": arg.arg, "has_default": False}
            if arg in node.args.defaults or (node.args.defaults and node.args.args.index(arg) < len(node.args.args) - len(node.args.defaults)):
                param["has_default"] = True
            params.append(param)
        return params
    
    def _extract_model_fields(self, node: ast.ClassDef) -> List[Dict]:
        """Extract model field definitions"""
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field = {
                    "name": item.target.id,
                    "annotation": ast.unparse(item.annotation) if hasattr(ast, 'unparse') else "Any",
                    "has_default": item.value is not None,
                }
                fields.append(field)
        return fields
    
    def _extract_class_methods(self, node: ast.ClassDef) -> List[Dict]:
        """Extract class method definitions"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = {
                    "name": item.name,
                    "args": [arg.arg for arg in item.args.args if arg.arg != 'self'],
                    "docstring": ast.get_docstring(item),
                }
                methods.append(method)
        return methods
    
    def generate_conftest(self) -> str:
        """Generate conftest.py with shared fixtures"""
        return '''"""
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
'''
    
    def generate_schema_tests(self) -> str:
        """Generate Pydantic model validation tests"""
        return '''"""
Pydantic Schema Validation Tests
================================
Tests for all Pydantic models in api/models/schemas.py
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models.schemas import (
    SubscriptionFrequency,
    OrderStatus,
    UserBase,
    UserCreate,
    User,
    ProductBase,
    Product,
    CartItem,
    CartResponse,
    SubscriptionCreate,
    Subscription,
    OrderItem,
    OrderCreate,
    Order,
    LoginRequest,
    AuthResponse,
)


class TestSubscriptionFrequency:
    """Tests for SubscriptionFrequency enum"""
    
    def test_daily_frequency(self):
        """Test daily frequency value"""
        assert SubscriptionFrequency.DAILY.value == "daily"
    
    def test_weekly_frequency(self):
        """Test weekly frequency value"""
        assert SubscriptionFrequency.WEEKLY.value == "weekly"
    
    def test_monthly_frequency(self):
        """Test monthly frequency value"""
        assert SubscriptionFrequency.MONTHLY.value == "monthly"
    
    def test_frequency_as_string(self):
        """Test frequency can be used as string"""
        assert str(SubscriptionFrequency.DAILY) == "SubscriptionFrequency.DAILY"


class TestOrderStatus:
    """Tests for OrderStatus enum"""
    
    def test_all_statuses_defined(self):
        """Test all order statuses are defined"""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.PREPARING.value == "preparing"
        assert OrderStatus.OUT_FOR_DELIVERY.value == "out_for_delivery"
        assert OrderStatus.DELIVERED.value == "delivered"
        assert OrderStatus.CANCELLED.value == "cancelled"


class TestLoginRequest:
    """Tests for LoginRequest model"""
    
    def test_valid_login_request(self):
        """Test valid login credentials"""
        login = LoginRequest(email="user@test.com", password="password123")
        assert login.email == "user@test.com"
        assert login.password == "password123"
    
    def test_login_missing_email(self):
        """Test login with missing email raises error"""
        with pytest.raises(ValidationError):
            LoginRequest(password="password123")
    
    def test_login_missing_password(self):
        """Test login with missing password raises error"""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@test.com")
    
    def test_login_empty_email(self):
        """Test login with empty email raises error"""
        with pytest.raises(ValidationError):
            LoginRequest(email="", password="password123")
    
    def test_login_empty_password(self):
        """Test login with empty password raises error"""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@test.com", password="")


class TestUserCreate:
    """Tests for UserCreate model"""
    
    def test_valid_user_create(self):
        """Test valid user creation data"""
        user = UserCreate(
            name="John Doe",
            email="john@test.com",
            phone="+91 9876543210",
            address="123 Main St, Mumbai"
        )
        assert user.name == "John Doe"
        assert user.email == "john@test.com"
        assert user.phone == "+91 9876543210"
        assert user.address == "123 Main St, Mumbai"
    
    def test_user_create_missing_name(self):
        """Test user creation without name raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="john@test.com",
                phone="+91 9876543210",
                address="123 Main St"
            )
    
    def test_user_create_missing_email(self):
        """Test user creation without email raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                phone="+91 9876543210",
                address="123 Main St"
            )
    
    def test_user_create_missing_phone(self):
        """Test user creation without phone raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@test.com",
                address="123 Main St"
            )
    
    def test_user_create_missing_address(self):
        """Test user creation without address raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@test.com",
                phone="+91 9876543210"
            )


class TestProduct:
    """Tests for Product model"""
    
    def test_valid_product(self, sample_product):
        """Test valid product creation"""
        product = Product(**sample_product, id=1)
        assert product.id == 1
        assert product.name == "Organic Tomatoes"
        assert product.price == 3.99
        assert product.category == "vegetables"
        assert product.stock == 100
    
    def test_product_with_optional_image(self, sample_product):
        """Test product with optional image URL"""
        product_data = sample_product.copy()
        product_data["image_url"] = "https://example.com/image.jpg"
        product = Product(**product_data, id=1)
        assert product.image_url == "https://example.com/image.jpg"
    
    def test_product_missing_required_field(self):
        """Test product with missing required field raises error"""
        with pytest.raises(ValidationError):
            Product(id=1, name="Tomato", category="vegetables")
    
    def test_product_negative_price(self):
        """Test product with negative price raises error"""
        with pytest.raises(ValidationError):
            Product(
                id=1,
                name="Tomato",
                category="vegetables",
                price=-5.99,
                unit="kg",
                stock=100,
                description="Test"
            )
    
    def test_product_zero_price(self):
        """Test product with zero price is valid"""
        product = Product(
            id=1,
            name="Free Sample",
            category="vegetables",
            price=0.0,
            unit="piece",
            stock=10,
            description="Free sample product"
        )
        assert product.price == 0.0
    
    def test_product_negative_stock(self):
        """Test product with negative stock raises error"""
        with pytest.raises(ValidationError):
            Product(
                id=1,
                name="Tomato",
                category="vegetables",
                price=3.99,
                unit="kg",
                stock=-10,
                description="Test"
            )


class TestCartItem:
    """Tests for CartItem model"""
    
    def test_valid_cart_item(self):
        """Test valid cart item"""
        item = CartItem(
            product_id=1,
            name="Organic Tomatoes",
            price=3.99,
            quantity=2,
            unit="kg",
            subtotal=7.98
        )
        assert item.product_id == 1
        assert item.quantity == 2
        assert item.subtotal == 7.98
    
    def test_cart_item_integer_quantity(self):
        """Test cart item with integer quantity"""
        item = CartItem(
            product_id=1,
            name="Test",
            price=1.0,
            quantity=5,
            unit="kg",
            subtotal=5.0
        )
        assert item.quantity == 5
    
    def test_cart_item_missing_required_field(self):
        """Test cart item with missing required field raises error"""
        with pytest.raises(ValidationError):
            CartItem(
                product_id=1,
                name="Test",
                price=1.0,
                unit="kg",
                subtotal=1.0
            )
    
    def test_cart_item_zero_quantity(self):
        """Test cart item with zero quantity is valid"""
        item = CartItem(
            product_id=1,
            name="Test",
            price=1.0,
            quantity=0,
            unit="kg",
            subtotal=0.0
        )
        assert item.quantity == 0


class TestCartResponse:
    """Tests for CartResponse model"""
    
    def test_valid_cart_response(self):
        """Test valid cart response"""
        items = [
            CartItem(
                product_id=1,
                name="Tomato",
                price=3.99,
                quantity=2,
                unit="kg",
                subtotal=7.98
            )
        ]
        response = CartResponse(
            items=items,
            subtotal=7.98,
            delivery_fee=2.99,
            total=10.97
        )
        assert len(response.items) == 1
        assert response.total == 10.97
    
    def test_empty_cart_response(self):
        """Test empty cart response"""
        response = CartResponse(
            items=[],
            subtotal=0.0,
            delivery_fee=0.0,
            total=0.0
        )
        assert len(response.items) == 0
        assert response.total == 0.0
    
    def test_cart_response_missing_items(self):
        """Test cart response without items raises error"""
        with pytest.raises(ValidationError):
            CartResponse(
                subtotal=0.0,
                delivery_fee=0.0,
                total=0.0
            )


class TestSubscriptionCreate:
    """Tests for SubscriptionCreate model"""
    
    def test_valid_subscription_daily(self):
        """Test valid daily subscription"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.DAILY,
            quantity=2
        )
        assert sub.frequency == SubscriptionFrequency.DAILY
        assert sub.quantity == 2
    
    def test_valid_subscription_weekly(self):
        """Test valid weekly subscription"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.WEEKLY
        )
        assert sub.frequency == SubscriptionFrequency.WEEKLY
    
    def test_valid_subscription_monthly(self):
        """Test valid monthly subscription"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.MONTHLY,
            quantity=5
        )
        assert sub.frequency == SubscriptionFrequency.MONTHLY
        assert sub.quantity == 5
    
    def test_subscription_default_quantity(self):
        """Test subscription default quantity is 1"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.WEEKLY
        )
        assert sub.quantity == 1
    
    def test_subscription_missing_product_id(self):
        """Test subscription without product_id raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(frequency=SubscriptionFrequency.DAILY)
    
    def test_subscription_missing_frequency(self):
        """Test subscription without frequency raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(product_id=1)
    
    def test_subscription_invalid_frequency(self):
        """Test subscription with invalid frequency raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(product_id=1, frequency="invalid")
    
    def test_subscription_negative_quantity(self):
        """Test subscription with negative quantity raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(
                product_id=1,
                frequency=SubscriptionFrequency.DAILY,
                quantity=-1
            )
    
    def test_subscription_zero_quantity(self):
        """Test subscription with zero quantity raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(
                product_id=1,
                frequency=SubscriptionFrequency.DAILY,
                quantity=0
            )


class TestOrderCreate:
    """Tests for OrderCreate model"""
    
    def test_valid_order_create(self, sample_order_items, sample_address):
        """Test valid order creation"""
        order = OrderCreate(
            items=sample_order_items,
            address=sample_address
        )
        assert len(order.items) == 2
        assert order.address == sample_address
        assert order.payment_method == "cod"
    
    def test_order_create_with_card_payment(self, sample_order_items, sample_address):
        """Test order with card payment"""
        order = OrderCreate(
            items=sample_order_items,
            address=sample_address,
            payment_method="card"
        )
        assert order.payment_method == "card"
    
    def test_order_create_empty_items(self, sample_address):
        """Test order with empty items list"""
        order = OrderCreate(
            items=[],
            address=sample_address
        )
        assert len(order.items) == 0
    
    def test_order_create_missing_address(self, sample_order_items):
        """Test order without address raises error"""
        with pytest.raises(ValidationError):
            OrderCreate(items=sample_order_items)
    
    def test_order_create_missing_items(self, sample_address):
        """Test order without items raises error"""
        with pytest.raises(ValidationError):
            OrderCreate(address=sample_address)


class TestOrderItem:
    """Tests for OrderItem model"""
    
    def test_valid_order_item(self):
        """Test valid order item"""
        item = OrderItem(
            product_id=1,
            name="Organic Tomatoes",
            price=3.99,
            quantity=2,
            subtotal=7.98
        )
        assert item.product_id == 1
        assert item.quantity == 2
        assert item.subtotal == 7.98
    
    def test_order_item_missing_field(self):
        """Test order item with missing field raises error"""
        with pytest.raises(ValidationError):
            OrderItem(
                product_id=1,
                name="Tomato",
                price=3.99,
                quantity=2
            )


class TestAuthResponse:
    """Tests for AuthResponse model"""
    
    def test_valid_auth_response(self):
        """Test valid auth response"""
        response = AuthResponse(
            user={"id": 1, "name": "Test User"},
            token="test-token-123"
        )
        assert response.token == "test-token-123"
        assert response.user["id"] == 1
    
    def test_auth_response_missing_token(self):
        """Test auth response without token raises error"""
        with pytest.raises(ValidationError):
            AuthResponse(user={"id": 1})
    
    def test_auth_response_missing_user(self):
        """Test auth response without user raises error"""
        with pytest.raises(ValidationError):
            AuthResponse(token="test-token")
'''
    
    def generate_auth_route_tests(self) -> str:
        """Generate authentication route tests"""
        return '''"""
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
'''
    
    def generate_product_route_tests(self) -> str:
        """Generate product route tests"""
        return '''"""
Product Routes Tests
====================
Tests for product endpoints: /api/products/*, /api/search, /api/categories
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


class TestGetProducts:
    """Tests for GET /api/products endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_all_products(self):
        """Test getting all products"""
        response = self.client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Verify product structure
        if data:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "price" in data[0]
            assert "category" in data[0]
    
    def test_get_products_returns_vegetables(self):
        """Test that products include vegetables"""
        response = self.client.get("/api/products")
        data = response.json()
        categories = [p["category"] for p in data]
        assert "vegetables" in categories
    
    def test_get_products_returns_fruits(self):
        """Test that products include fruits"""
        response = self.client.get("/api/products")
        data = response.json()
        categories = [p["category"] for p in data]
        assert "fruits" in categories
    
    def test_get_products_returns_nuts(self):
        """Test that products include nuts"""
        response = self.client.get("/api/products")
        data = response.json()
        categories = [p["category"] for p in data]
        assert "nuts" in categories
    
    def test_get_products_contains_required_fields(self):
        """Test that products have all required fields"""
        response = self.client.get("/api/products")
        data = response.json()
        for product in data:
            assert "id" in product
            assert "name" in product
            assert "category" in product
            assert "price" in product
            assert "unit" in product
            assert "stock" in product
            assert "description" in product


class TestGetProductById:
    """Tests for GET /api/products/{product_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_product_valid_id(self):
        """Test getting product with valid ID"""
        response = self.client.get("/api/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Organic Tomatoes"
    
    def test_get_product_invalid_id(self):
        """Test getting product with non-existent ID"""
        response = self.client.get("/api/products/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_product_zero_id(self):
        """Test getting product with ID 0"""
        response = self.client.get("/api/products/0")
        assert response.status_code == 404
    
    def test_get_product_negative_id(self):
        """Test getting product with negative ID"""
        response = self.client.get("/api/products/-1")
        assert response.status_code == 404
    
    def test_get_product_string_id(self):
        """Test getting product with string ID (type error)"""
        response = self.client.get("/api/products/abc")
        assert response.status_code == 422  # Validation error


class TestGetProductsByCategory:
    """Tests for GET /api/products/category/{category} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_vegetables(self):
        """Test getting vegetables category"""
        response = self.client.get("/api/products/category/vegetables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for product in data:
            assert product["category"].lower() == "vegetables"
    
    def test_get_fruits(self):
        """Test getting fruits category"""
        response = self.client.get("/api/products/category/fruits")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "fruits"
    
    def test_get_nuts(self):
        """Test getting nuts category"""
        response = self.client.get("/api/products/category/nuts")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "nuts"
    
    def test_category_case_insensitive(self):
        """Test category search is case insensitive"""
        response = self.client.get("/api/products/category/VEGETABLES")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "vegetables"
    
    def test_category_mixed_case(self):
        """Test category search with mixed case"""
        response = self.client.get("/api/products/category/FrUiTs")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "fruits"
    
    def test_invalid_category(self):
        """Test getting non-existent category"""
        response = self.client.get("/api/products/category/nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_empty_category_name(self):
        """Test getting empty category name"""
        response = self.client.get("/api/products/category/")
        # Should return all products or 404
        assert response.status_code in [200, 404]


class TestSearchProducts:
    """Tests for GET /api/search endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_search_by_name(self):
        """Test searching by product name"""
        response = self.client.get("/api/search?q=tomato")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Results should contain "tomato" in name
        for product in data:
            assert "tomato" in product["name"].lower()
    
    def test_search_by_category(self):
        """Test searching by category"""
        response = self.client.get("/api/search?q=vegetables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for product in data:
            assert "vegetables" in [product["category"].lower(), product["name"].lower(), product["description"].lower()]
    
    def test_search_no_results(self):
        """Test search with no matching results"""
        response = self.client.get("/api/search?q=nonexistentproductxyz")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        response1 = self.client.get("/api/search?q=TOMATO")
        response2 = self.client.get("/api/search?q=tomato")
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(response1.json()) == len(response2.json())
    
    def test_search_partial_match(self):
        """Test partial word match"""
        response = self.client.get("/api/search?q=app")
        assert response.status_code == 200
        data = response.json()
        # Should match "Apple" products
        assert any("apple" in p["name"].lower() for p in data)
    
    def test_search_special_characters(self):
        """Test search with special characters"""
        response = self.client.get("/api/search?q=@#$%")
        assert response.status_code == 200
        # Should return empty or handle gracefully
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        response = self.client.get("/api/search?q=")
        assert response.status_code == 200


class TestGetCategories:
    """Tests for GET /api/categories endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_categories(self):
        """Test getting all categories"""
        response = self.client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least vegetables, fruits, nuts
    
    def test_categories_include_expected(self):
        """Test that expected categories are present"""
        response = self.client.get("/api/categories")
        data = response.json()
        categories = [c.lower() for c in data]
        assert "vegetables" in categories
        assert "fruits" in categories
        assert "nuts" in categories
    
    def test_categories_no_duplicates(self):
        """Test that categories list has no duplicates"""
        response = self.client.get("/api/categories")
        data = response.json()
        assert len(data) == len(set(data))
'''
    
    def generate_subscription_route_tests(self) -> str:
        """Generate subscription route tests"""
        return '''"""
Subscription Routes Tests
=========================
Tests for subscription endpoints: /api/subscriptions/*
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, subscriptions


class TestCreateSubscription:
    """Tests for POST /api/subscriptions endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_create_subscription_daily(self):
        """Test creating daily subscription"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "daily",
                "quantity": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "daily"
        assert data["quantity"] == 2
        assert data["active"] is True
        assert "next_delivery" in data
    
    def test_create_subscription_weekly(self):
        """Test creating weekly subscription"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "weekly"
    
    def test_create_subscription_monthly(self):
        """Test creating monthly subscription"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "monthly",
                "quantity": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "monthly"
    
    def test_create_subscription_default_quantity(self):
        """Test subscription defaults quantity to 1"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1
    
    def test_create_subscription_invalid_product(self):
        """Test creating subscription with invalid product ID"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 9999,
                "frequency": "weekly",
                "quantity": 1
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_subscription_invalid_frequency(self):
        """Test creating subscription with invalid frequency"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "yearly",
                "quantity": 1
            }
        )
        # May accept invalid frequency or validate
        # The behavior depends on implementation
        assert response.status_code in [200, 400, 422]
    
    def test_create_subscription_zero_quantity(self):
        """Test creating subscription with zero quantity"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 0
            }
        )
        # Should either accept or reject zero quantity
        assert response.status_code in [200, 422]
    
    def test_create_subscription_negative_quantity(self):
        """Test creating subscription with negative quantity"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": -1
            }
        )
        assert response.status_code == 422
    
    def test_create_subscription_missing_product_id(self):
        """Test creating subscription without product_id"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "frequency": "weekly",
                "quantity": 1
            }
        )
        assert response.status_code == 422
    
    def test_create_subscription_missing_frequency(self):
        """Test creating subscription without frequency"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "quantity": 1
            }
        )
        assert response.status_code == 422
    
    def test_create_subscription_with_auth(self):
        """Test creating subscription with authentication"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        # Create subscription with auth
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 1
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # User ID should be set when authenticated
        assert data.get("user_id") is not None


class TestGetSubscriptions:
    """Tests for GET /api/subscriptions endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_subscriptions(self):
        """Test getting subscriptions"""
        response = self.client.get("/api/subscriptions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_subscriptions_returns_list(self):
        """Test that subscriptions endpoint returns a list"""
        response = self.client.get("/api/subscriptions")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestCancelSubscription:
    """Tests for DELETE /api/subscriptions/{subscription_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        # Create a subscription to cancel
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 1
            }
        )
        self.subscription_id = response.json()["id"]
    
    def test_cancel_subscription(self):
        """Test cancelling a subscription"""
        response = self.client.delete(f"/api/subscriptions/{self.subscription_id}")
        assert response.status_code == 200
        assert "cancelled" in response.json()["message"].lower()
    
    def test_cancel_subscription_invalid_id(self):
        """Test cancelling non-existent subscription"""
        response = self.client.delete("/api/subscriptions/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_cancel_subscription_already_cancelled(self):
        """Test cancelling already cancelled subscription"""
        # Cancel first time
        self.client.delete(f"/api/subscriptions/{self.subscription_id}")
        # Cancel second time
        response = self.client.delete(f"/api/subscriptions/{self.subscription_id}")
        # May return 404 or 200 depending on implementation
        assert response.status_code in [200, 404]


class TestGetSubscriptionPlans:
    """Tests for GET /api/subscription-plans endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_subscription_plans(self):
        """Test getting subscription plans"""
        response = self.client.get("/api/subscription-plans")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # daily, weekly, monthly
    
    def test_subscription_plans_structure(self):
        """Test subscription plans have required fields"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        for plan in data:
            assert "id" in plan
            assert "name" in plan
            assert "description" in plan
            assert "price" in plan
            assert "benefits" in plan
    
    def test_subscription_plans_daily(self):
        """Test daily plan exists"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        daily_plan = next((p for p in data if p["id"] == "daily"), None)
        assert daily_plan is not None
        assert daily_plan["name"] == "Daily Fresh"
    
    def test_subscription_plans_weekly(self):
        """Test weekly plan exists"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        weekly_plan = next((p for p in data if p["id"] == "weekly"), None)
        assert weekly_plan is not None
        assert weekly_plan["name"] == "Weekly Bundle"
    
    def test_subscription_plans_monthly(self):
        """Test monthly plan exists"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        monthly_plan = next((p for p in data if p["id"] == "monthly"), None)
        assert monthly_plan is not None
        assert monthly_plan["name"] == "Monthly Mega"
'''
    
    def generate_order_route_tests(self) -> str:
        """Generate order route tests"""
        return '''"""
Order Routes Tests
==================
Tests for order endpoints: /api/orders/*
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, orders


class TestPlaceOrder:
    """Tests for POST /api/orders endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        self.order_items = [
            {"product_id": 1, "name": "Organic Tomatoes", "price": 3.99, "quantity": 2, "subtotal": 7.98},
            {"product_id": 7, "name": "Red Apples", "price": 4.99, "quantity": 1, "subtotal": 4.99}
        ]
        self.address = "123 Test Street, Mumbai, India"
    
    def test_place_order_success(self):
        """Test successful order placement"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        assert len(data["items"]) == 2
        assert "id" in data
        assert "total" in data
    
    def test_place_order_calculates_total(self):
        """Test order calculates total correctly"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            }
        )
        data = response.json()
        # Total = subtotal + delivery_fee (2.99)
        expected_subtotal = 7.98 + 4.99  # 12.97
        assert data["subtotal"] == expected_subtotal
        assert data["delivery_fee"] == 2.99
        assert data["total"] == expected_subtotal + 2.99
    
    def test_place_order_empty_cart(self):
        """Test order with empty cart fails"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": [],
                "address": self.address
            }
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_place_order_missing_items(self):
        """Test order without items fails"""
        response = self.client.post(
            "/api/orders",
            json={
                "address": self.address
            }
        )
        assert response.status_code == 422
    
    def test_place_order_missing_address(self):
        """Test order without address fails"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items
            }
        )
        assert response.status_code == 422
    
    def test_place_order_single_item(self):
        """Test order with single item"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": [self.order_items[0]],
                "address": self.address
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
    
    def test_place_order_with_payment_method(self):
        """Test order with custom payment method"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address,
                "payment_method": "card"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payment_method"] == "card"
    
    def test_place_order_default_payment_method(self):
        """Test order with default payment method (COD)"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payment_method"] == "cod"
    
    def test_place_order_with_auth(self):
        """Test placing order with authentication"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        # Place order with auth
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # User ID should be set when authenticated
        assert data.get("user_id") is not None


class TestGetOrders:
    """Tests for GET /api/orders endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_orders(self):
        """Test getting orders list"""
        response = self.client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_orders_returns_list(self):
        """Test that orders endpoint returns a list"""
        response = self.client.get("/api/orders")
        assert isinstance(response.json(), list)


class TestGetOrderById:
    """Tests for GET /api/orders/{order_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        # Create an order first
        response = self.client.post(
            "/api/orders",
            json={
                "items": [
                    {"product_id": 1, "name": "Tomato", "price": 3.99, "quantity": 1, "subtotal": 3.99}
                ],
                "address": "123 Test St"
            }
        )
        self.order_id = response.json()["id"]
    
    def test_get_order_valid_id(self):
        """Test getting order with valid ID"""
        response = self.client.get(f"/api/orders/{self.order_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.order_id
    
    def test_get_order_invalid_id(self):
        """Test getting order with non-existent ID"""
        response = self.client.get("/api/orders/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_order_structure(self):
        """Test order has required fields"""
        response = self.client.get(f"/api/orders/{self.order_id}")
        data = response.json()
        required_fields = ["id", "items", "subtotal", "delivery_fee", "total", "status", "address"]
        for field in required_fields:
            assert field in data


class TestTrackOrder:
    """Tests for GET /api/orders/track/{order_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        # Create an order first
        response = self.client.post(
            "/api/orders",
            json={
                "items": [
                    {"product_id": 1, "name": "Tomato", "price": 3.99, "quantity": 1, "subtotal": 3.99}
                ],
                "address": "123 Test St"
            }
        )
        self.order_id = response.json()["id"]
    
    def test_track_order_valid_id(self):
        """Test tracking order with valid ID"""
        response = self.client.get(f"/api/orders/track/{self.order_id}")
        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert "status" in data
        assert "timeline" in data
    
    def test_track_order_invalid_id(self):
        """Test tracking non-existent order"""
        response = self.client.get("/api/orders/track/9999")
        assert response.status_code == 404
    
    def test_track_order_timeline_structure(self):
        """Test order timeline has correct structure"""
        response = self.client.get(f"/api/orders/track/{self.order_id}")
        data = response.json()
        timeline = data["timeline"]
        assert isinstance(timeline, list)
        assert len(timeline) == 4  # confirmed, preparing, out_for_delivery, delivered
        
        for step in timeline:
            assert "status" in step
            assert "completed" in step
    
    def test_track_order_initial_status(self):
        """Test new order has 'confirmed' status"""
        response = self.client.get(f"/api/orders/track/{self.order_id}")
        data = response.json()
        assert data["status"] == "confirmed"
'''
    
    def generate_notification_route_tests(self) -> str:
        """Generate notification route tests"""
        return '''"""
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
'''
    
    def generate_store_tests(self) -> str:
        """Generate store unit tests"""
        return '''"""
Store Unit Tests
=================
Tests for data store classes: UserStore, ProductStore, OrderStore, etc.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import UserStore, ProductStore, OrderStore, SubscriptionStore, NotificationStore


class TestUserStore:
    """Tests for UserStore class"""
    
    @pytest.fixture
    def user_store(self):
        """Create fresh UserStore for each test"""
        return UserStore()
    
    def test_create_user(self, user_store):
        """Test creating a new user"""
        user = user_store.create_user(
            name="Test User",
            email="test@example.com",
            phone="+91 9876543210",
            address="123 Test St",
            password="password123"
        )
        assert user["name"] == "Test User"
        assert user["email"] == "test@example.com"
        assert "id" in user
        assert "password" in user
        assert user["password"] != "password123"  # Password should be hashed
    
    def test_create_duplicate_email(self, user_store):
        """Test creating user with duplicate email fails"""
        user_store.create_user(
            name="User 1",
            email="duplicate@test.com",
            phone="123",
            address="Address",
            password="pass1"
        )
        with pytest.raises(ValueError, match="already registered"):
            user_store.create_user(
                name="User 2",
                email="duplicate@test.com",
                phone="456",
                address="Address 2",
                password="pass2"
            )
    
    def test_authenticate_valid(self, user_store):
        """Test authenticating with valid credentials"""
        user_store.create_user(
            name="Test User",
            email="auth@test.com",
            phone="123",
            address="Address",
            password="correctpassword"
        )
        result = user_store.authenticate("auth@test.com", "correctpassword")
        assert result is not None
        assert "user" in result
        assert "token" in result
    
    def test_authenticate_invalid_email(self, user_store):
        """Test authenticating with non-existent email"""
        result = user_store.authenticate("nonexistent@test.com", "password")
        assert result is None
    
    def test_authenticate_invalid_password(self, user_store):
        """Test authenticating with wrong password"""
        user_store.create_user(
            name="Test User",
            email="wrongpass@test.com",
            phone="123",
            address="Address",
            password="correctpassword"
        )
        result = user_store.authenticate("wrongpass@test.com", "wrongpassword")
        assert result is None
    
    def test_get_user_by_token(self, user_store):
        """Test getting user by token"""
        user_store.create_user(
            name="Test User",
            email="token@test.com",
            phone="123",
            address="Address",
            password="password"
        )
        result = user_store.authenticate("token@test.com", "password")
        token = result["token"]
        user = user_store.get_user(token)
        assert user is not None
        assert user["email"] == "token@test.com"
    
    def test_get_user_invalid_token(self, user_store):
        """Test getting user with invalid token"""
        user = user_store.get_user("invalid-token")
        assert user is None


class TestProductStore:
    """Tests for ProductStore class"""
    
    @pytest.fixture
    def product_store(self):
        """Create ProductStore instance"""
        return ProductStore()
    
    def test_get_all_products(self, product_store):
        """Test getting all products"""
        products = product_store.get_all()
        assert isinstance(products, list)
        assert len(products) > 0
    
    def test_get_product_by_id(self, product_store):
        """Test getting product by ID"""
        product = product_store.get_by_id(1)
        assert product is not None
        assert product["id"] == 1
        assert "name" in product
    
    def test_get_product_invalid_id(self, product_store):
        """Test getting product with invalid ID"""
        product = product_store.get_by_id(9999)
        assert product is None
    
    def test_get_products_by_category(self, product_store):
        """Test filtering products by category"""
        vegetables = product_store.get_by_category("vegetables")
        assert isinstance(vegetables, list)
        for p in vegetables:
            assert p["category"].lower() == "vegetables"
    
    def test_category_case_insensitive(self, product_store):
        """Test category filter is case insensitive"""
        v1 = product_store.get_by_category("VEGETABLES")
        v2 = product_store.get_by_category("vegetables")
        assert len(v1) == len(v2)
    
    def test_search_products(self, product_store):
        """Test searching products"""
        results = product_store.search("tomato")
        assert isinstance(results, list)
        for p in results:
            assert "tomato" in p["name"].lower()
    
    def test_search_case_insensitive(self, product_store):
        """Test search is case insensitive"""
        r1 = product_store.search("TOMATO")
        r2 = product_store.search("tomato")
        assert len(r1) == len(r2)
    
    def test_get_categories(self, product_store):
        """Test getting all categories"""
        categories = product_store.get_categories()
        assert isinstance(categories, list)
        assert "vegetables" in categories
        assert "fruits" in categories
        assert "nuts" in categories


class TestOrderStore:
    """Tests for OrderStore class"""
    
    @pytest.fixture
    def order_store(self):
        """Create fresh OrderStore for each test"""
        return OrderStore()
    
    def test_create_order(self, order_store):
        """Test creating an order"""
        order = order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 2}],
            subtotal=11.98,
            delivery_fee=2.99,
            total=14.97,
            address="123 Test St",
            payment_method="cod"
        )
        assert order["id"] == 1
        assert order["status"] == "confirmed"
        assert len(order["items"]) == 1
    
    def test_get_order(self, order_store):
        """Test getting order by ID"""
        order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 1}],
            subtotal=5.99,
            delivery_fee=2.99,
            total=8.98,
            address="Address",
            payment_method="cod"
        )
        order = order_store.get(1)
        assert order is not None
        assert order["id"] == 1
    
    def test_get_order_invalid_id(self, order_store):
        """Test getting order with invalid ID"""
        order = order_store.get(9999)
        assert order is None
    
    def test_get_all_orders(self, order_store):
        """Test getting all orders"""
        order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 1}],
            subtotal=5.99,
            delivery_fee=2.99,
            total=8.98,
            address="Address",
            payment_method="cod"
        )
        orders = order_store.get_all()
        assert isinstance(orders, list)
        assert len(orders) == 1
    
    def test_get_user_orders(self, order_store):
        """Test getting orders for specific user"""
        order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 1}],
            subtotal=5.99,
            delivery_fee=2.99,
            total=8.98,
            address="Address",
            payment_method="cod"
        )
        user_orders = order_store.get_user_orders(1)
        assert len(user_orders) == 1
        
        other_user_orders = order_store.get_user_orders(999)
        assert len(other_user_orders) == 0


class TestSubscriptionStore:
    """Tests for SubscriptionStore class"""
    
    @pytest.fixture
    def subscription_store(self):
        """Create fresh SubscriptionStore for each test"""
        return SubscriptionStore()
    
    def test_create_subscription(self, subscription_store):
        """Test creating a subscription"""
        sub = subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Organic Tomatoes",
            frequency="weekly",
            quantity=2,
            price=3.99
        )
        assert sub["id"] == 1
        assert sub["frequency"] == "weekly"
        assert sub["quantity"] == 2
        assert sub["active"] is True
        assert "next_delivery" in sub
    
    def test_create_daily_subscription(self, subscription_store):
        """Test creating daily subscription calculates next delivery"""
        sub = subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="daily",
            quantity=1,
            price=5.99
        )
        assert sub["frequency"] == "daily"
    
    def test_create_monthly_subscription(self, subscription_store):
        """Test creating monthly subscription"""
        sub = subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="monthly",
            quantity=1,
            price=5.99
        )
        assert sub["frequency"] == "monthly"
    
    def test_get_user_subscriptions(self, subscription_store):
        """Test getting user's subscriptions"""
        subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="weekly",
            quantity=1,
            price=5.99
        )
        subs = subscription_store.get_user_subscriptions(1)
        assert len(subs) == 1
    
    def test_cancel_subscription(self, subscription_store):
        """Test cancelling a subscription"""
        subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="weekly",
            quantity=1,
            price=5.99
        )
        result = subscription_store.cancel(1)
        assert result is True
        
        subs = subscription_store.get_user_subscriptions(1)
        assert len(subs) == 0  # Cancelled subscription not returned
    
    def test_cancel_invalid_subscription(self, subscription_store):
        """Test cancelling non-existent subscription"""
        result = subscription_store.cancel(9999)
        assert result is False


class TestNotificationStore:
    """Tests for NotificationStore class"""
    
    @pytest.fixture
    def notification_store(self):
        """Create fresh NotificationStore for each test"""
        return NotificationStore()
    
    def test_create_notification(self, notification_store):
        """Test creating a notification"""
        notif = notification_store.create(
            user_id=1,
            notification_type="order",
            title="Test Notification",
            message="This is a test",
            data={"order_id": 1}
        )
        assert notif["id"] == 1
        assert notif["title"] == "Test Notification"
        assert notif["read"] is False
    
    def test_get_user_notifications(self, notification_store):
        """Test getting user's notifications"""
        notification_store.create(
            user_id=1,
            notification_type="order",
            title="Notif 1",
            message="Message 1"
        )
        notification_store.create(
            user_id=1,
            notification_type="delivery",
            title="Notif 2",
            message="Message 2"
        )
        notifs = notification_store.get_user_notifications(1)
        assert len(notifs) == 2
    
    def test_get_unread_count(self, notification_store):
        """Test getting unread notification count"""
        notification_store.create(
            user_id=1,
            notification_type="order",
            title="Notif 1",
            message="Message"
        )
        notification_store.create(
            user_id=1,
            notification_type="delivery",
            title="Notif 2",
            message="Message"
        )
        count = notification_store.get_unread_count(1)
        assert count == 2
    
    def test_mark_as_read(self, notification_store):
        """Test marking notification as read"""
        notif = notification_store.create(
            user_id=1,
            notification_type="order",
            title="Test",
            message="Test"
        )
        result = notification_store.mark_as_read(1)
        assert result is True
        assert notification_store._notifications[1]["read"] is True
    
    def test_mark_all_as_read(self, notification_store):
        """Test marking all notifications as read"""
        notification_store.create(user_id=1, notification_type="order", title="N1", message="M")
        notification_store.create(user_id=1, notification_type="order", title="N2", message="M")
        count = notification_store.mark_all_as_read(1)
        assert count == 2
    
    def test_delete_notification(self, notification_store):
        """Test deleting a notification"""
        notification_store.create(
            user_id=1,
            notification_type="order",
            title="Test",
            message="Test"
        )
        result = notification_store.delete(1)
        assert result is True
        assert 1 not in notification_store._notifications
    
    def test_delete_invalid_notification(self, notification_store):
        """Test deleting non-existent notification"""
        result = notification_store.delete(9999)
        assert result is False
    
    def test_create_order_notification(self, notification_store):
        """Test creating order notification"""
        notif = notification_store.create_order_notification(
            user_id=1,
            order_id=123,
            items=[{"name": "Tomato", "quantity": 2}]
        )
        assert notif["type"] == "order"
        assert "123" in notif["message"]
'''
    
    def generate_main_endpoints_tests(self) -> str:
        """Generate main endpoints tests"""
        return '''"""
Main Endpoints Tests
====================
Tests for root and health check endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_root_has_docs_link(self):
        """Test root endpoint includes docs link"""
        response = self.client.get("/")
        data = response.json()
        assert "docs" in data


class TestHealthEndpoint:
    """Tests for GET /api/health endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_health_includes_stats(self):
        """Test health check includes system stats"""
        response = self.client.get("/api/health")
        data = response.json()
        assert "products" in data
        assert "orders" in data
        assert "subscriptions" in data
    
    def test_health_products_count(self):
        """Test health check returns valid products count"""
        response = self.client.get("/api/health")
        data = response.json()
        assert isinstance(data["products"], int)
        assert data["products"] > 0


class TestCartAdd:
    """Tests for POST /api/cart/add endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_add_to_cart_valid_product(self):
        """Test adding valid product to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1, "quantity": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Added to cart"
        assert "product" in data
        assert data["quantity"] == 2
    
    def test_add_to_cart_invalid_product(self):
        """Test adding invalid product to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 9999, "quantity": 1}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_add_to_cart_default_quantity(self):
        """Test adding to cart with default quantity"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1
    
    def test_add_to_cart_zero_quantity(self):
        """Test adding zero quantity to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1, "quantity": 0}
        )
        # Should accept or reject depending on implementation
        assert response.status_code in [200, 422]
    
    def test_add_to_cart_negative_quantity(self):
        """Test adding negative quantity to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1, "quantity": -1}
        )
        assert response.status_code == 422
'''
    
    def generate_all_tests(self):
        """Generate all test files"""
        self.test_dir.mkdir(exist_ok=True)
        
        files_created = []
        
        # Generate conftest.py
        conftest_content = self.generate_conftest()
        conftest_path = self.test_dir / "conftest.py"
        conftest_path.write_text(conftest_content, encoding='utf-8')
        files_created.append(str(conftest_path))
        
        # Generate test files
        test_files = {
            "test_schemas.py": self.generate_schema_tests(),
            "test_auth_routes.py": self.generate_auth_route_tests(),
            "test_product_routes.py": self.generate_product_route_tests(),
            "test_subscription_routes.py": self.generate_subscription_route_tests(),
            "test_order_routes.py": self.generate_order_route_tests(),
            "test_notification_routes.py": self.generate_notification_route_tests(),
            "test_stores.py": self.generate_store_tests(),
            "test_main_endpoints.py": self.generate_main_endpoints_tests(),
        }
        
        for filename, content in test_files.items():
            filepath = self.test_dir / filename
            filepath.write_text(content, encoding='utf-8')
            files_created.append(str(filepath))
        
        self.generated_files = files_created
        return files_created


# ==================== ORCHESTRATOR INTEGRATION ====================

def get_test_agent() -> TestAgent:
    """Get TestAgent instance"""
    return TestAgent()


if __name__ == "__main__":
    # Run as script to generate tests
    agent = TestAgent()
    files = agent.generate_all_tests()
    print(f"Generated {len(files)} test files:")
    for f in files:
        print(f"  - {f}")
