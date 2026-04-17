"""
FreshCart AI - Models Module
"""

from pydantic import BaseModel
from pydantic import Field 
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubscriptionFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# ==================== USER MODELS ====================

class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime


# ==================== PRODUCT MODELS ====================

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    unit: str
    stock: int
    description: str
    image_url: Optional[str] = None


class Product(ProductBase):
    id: int


# ==================== CART MODELS ====================

class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    unit: str
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItem]
    subtotal: float
    delivery_fee: float
    total: float


# ==================== SUBSCRIPTION MODELS ====================

class SubscriptionCreate(BaseModel):
    product_id: int
    frequency: SubscriptionFrequency
    quantity: int = 1


class Subscription(BaseModel):
    id: int
    user_id: Optional[int]
    product_id: int
    product_name: str
    frequency: SubscriptionFrequency
    quantity: int
    price: float
    total: float
    next_delivery: str
    active: bool
    created_at: str


class SubscriptionRequest(BaseModel):
    product_id: int
    frequency: str
    quantity: int = Field(..., ge=1) 
# ==================== ORDER MODELS ====================

class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float


class OrderCreate(BaseModel):
    items: List[dict]
    address: str
    payment_method: str = "cod"


class Order(BaseModel):
    id: int
    user_id: Optional[int]
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float
    total: float
    status: OrderStatus
    address: str
    payment_method: str
    created_at: str
    estimated_delivery: str


# ==================== AUTH MODELS ====================

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1) 
    email: str
    phone: str
    address: str
    password: str  


class AuthResponse(BaseModel):
    user: dict
    token: str
