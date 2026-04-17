"""
Pydantic Models for FreshCart AI API
"""

from pydantic import BaseModel
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


class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str 


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    user: dict
    token: str
