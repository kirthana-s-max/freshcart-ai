"""
Product Routes - Products, Orders, Subscriptions
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

router = APIRouter(tags=["Products & Orders"])

# In-memory stores
_products = []
_orders = {}
_next_order_id = 1
_subscriptions = {}
_next_sub_id = 1


def _load_products():
    """Load products from CSV"""
    path = Path("data/products.csv")
    if path.exists():
        df = pd.read_csv(path)
        return df.to_dict('records')
    return _default_products()


def _default_products():
    """Default product catalog"""
    return [
        {"id": 1, "name": "Organic Tomatoes", "category": "vegetables", "price": 3.99, "unit": "kg", "stock": 100, "description": "Farm fresh organic tomatoes", "image_url": "https://images.unsplash.com/photo-1546470427-227c7b3f8311?w=400"},
        {"id": 2, "name": "Fresh Spinach", "category": "vegetables", "price": 2.49, "unit": "bunch", "stock": 80, "description": "Green leafy spinach", "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400"},
        {"id": 3, "name": "Organic Carrots", "category": "vegetables", "price": 1.99, "unit": "kg", "stock": 120, "description": "Sweet organic carrots", "image_url": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400"},
        {"id": 4, "name": "Fresh Broccoli", "category": "vegetables", "price": 2.99, "unit": "kg", "stock": 75, "description": "Green broccoli heads", "image_url": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400"},
        {"id": 5, "name": "Crisp Cucumbers", "category": "vegetables", "price": 1.49, "unit": "kg", "stock": 90, "description": "Fresh crunchy cucumbers", "image_url": "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400"},
        {"id": 6, "name": "Bell Peppers", "category": "vegetables", "price": 3.49, "unit": "kg", "stock": 60, "description": "Colorful bell peppers", "image_url": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400"},
        {"id": 7, "name": "Red Apples", "category": "fruits", "price": 4.99, "unit": "kg", "stock": 200, "description": "Crisp red apples", "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400"},
        {"id": 8, "name": "Organic Bananas", "category": "fruits", "price": 1.99, "unit": "dozen", "stock": 300, "description": "Ripe organic bananas", "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400"},
        {"id": 9, "name": "Fresh Oranges", "category": "fruits", "price": 3.99, "unit": "kg", "stock": 180, "description": "Juicy sweet oranges", "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?w=400"},
        {"id": 10, "name": "Seedless Grapes", "category": "fruits", "price": 5.99, "unit": "kg", "stock": 120, "description": "Sweet seedless grapes", "image_url": "https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=400"},
        {"id": 11, "name": "Fresh Strawberries", "category": "fruits", "price": 6.99, "unit": "box", "stock": 90, "description": "Organic strawberries", "image_url": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400"},
        {"id": 12, "name": "Sweet Mangoes", "category": "fruits", "price": 4.49, "unit": "kg", "stock": 100, "description": "Alphonso mangoes", "image_url": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400"},
        {"id": 13, "name": "Organic Almonds", "category": "nuts", "price": 12.99, "unit": "kg", "stock": 60, "description": "Raw organic almonds", "image_url": "https://images.unsplash.com/photo-1508061253366-f7da158b6d46?w=400"},
        {"id": 14, "name": "Walnuts", "category": "nuts", "price": 14.99, "unit": "kg", "stock": 50, "description": "Fresh shelled walnuts", "image_url": "https://images.unsplash.com/photo-1599593752329-26b651e2efcc?w=400"},
        {"id": 15, "name": "Roasted Cashews", "category": "nuts", "price": 15.99, "unit": "kg", "stock": 45, "description": "Premium roasted cashews", "image_url": "https://images.unsplash.com/photo-1630431341973-02e1b662ec35?w=400"},
        {"id": 16, "name": "Salted Pistachios", "category": "nuts", "price": 13.99, "unit": "kg", "stock": 55, "description": "Roasted pistachios", "image_url": "https://images.unsplash.com/photo-1594942895212-a1b77f48ee92?w=400"},
    ]


# Load products on module init
_products = _load_products()


# ==================== PRODUCTS ====================

@router.get("/api/products")
async def get_products():
    """Get all products"""
    return _products


@router.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Get a single product"""
    product = next((p for p in _products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/api/products/category/{category}")
async def get_by_category(category: str):
    """Get products by category"""
    return [p for p in _products if p["category"].lower() == category.lower()]


@router.get("/api/search")
async def search_products(q: str = Query(..., description="Search query")):
    """Search products"""
    query = q.lower()
    return [
        p for p in _products
        if query in p["name"].lower() or query in p["category"].lower() or query in p["description"].lower()
    ]


@router.get("/api/categories")
async def get_categories():
    """Get all categories"""
    return list(set(p["category"] for p in _products))


# ==================== CART ====================

@router.post("/api/cart/add")
async def add_to_cart(product_id: int, quantity: int = 1):
    """Add item to cart"""
    product = next((p for p in _products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Added to cart", "product": product, "quantity": quantity}


# ==================== SUBSCRIPTIONS ====================

@router.post("/api/subscriptions")
async def create_subscription(
    product_id: int,
    frequency: str,
    quantity: int = 1,
    authorization: Optional[str] = Header(None)
):
    """Create a new subscription"""
    global _next_sub_id
    
    product = next((p for p in _products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    days = {"daily": 1, "weekly": 7, "monthly": 30}.get(frequency, 7)
    
    subscription = {
        "id": _next_sub_id,
        "user_id": None,
        "product_id": product_id,
        "product_name": product["name"],
        "frequency": frequency,
        "quantity": quantity,
        "price": product["price"],
        "total": product["price"] * quantity,
        "next_delivery": (datetime.now() + timedelta(days=days)).isoformat(),
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    
    _subscriptions[_next_sub_id] = subscription
    _next_sub_id += 1
    
    return subscription


@router.get("/api/subscriptions")
async def get_subscriptions(authorization: Optional[str] = Header(None)):
    """Get subscriptions"""
    return list(_subscriptions.values())


@router.delete("/api/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: int):
    """Cancel a subscription"""
    if subscription_id not in _subscriptions:
        raise HTTPException(status_code=404, detail="Subscription not found")
    _subscriptions[subscription_id]["active"] = False
    return {"message": "Subscription cancelled"}


@router.get("/api/subscription-plans")
async def get_plans():
    """Get subscription plans"""
    return [
        {"id": "daily", "name": "Daily Fresh", "icon": "📅", "price": 9, "benefits": ["Daily delivery", "Always fresh", "Flexible skip days"]},
        {"id": "weekly", "name": "Weekly Bundle", "icon": "📦", "price": 19, "benefits": ["Weekly delivery", "10% off", "Free delivery", "Skip anytime"]},
        {"id": "monthly", "name": "Monthly Mega", "icon": "🎁", "price": 29, "benefits": ["Monthly delivery", "20% off", "Priority support", "Free delivery"]},
    ]


# ==================== ORDERS ====================

@router.post("/api/orders")
async def place_order(
    items: List[dict],
    address: str,
    payment_method: str = "cod",
    authorization: Optional[str] = Header(None)
):
    """Place a new order"""
    global _next_order_id
    
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    delivery_fee = 2.99
    total = subtotal + delivery_fee
    
    order_items = [
        {
            "product_id": item["product_id"],
            "name": item["name"],
            "price": item["price"],
            "quantity": item["quantity"],
            "subtotal": item["price"] * item["quantity"]
        }
        for item in items
    ]
    
    order = {
        "id": _next_order_id,
        "user_id": None,
        "items": order_items,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "status": "confirmed",
        "address": address,
        "payment_method": payment_method,
        "created_at": datetime.now().isoformat(),
        "estimated_delivery": (datetime.now() + timedelta(hours=45)).isoformat()
    }
    
    _orders[_next_order_id] = order
    _next_order_id += 1
    
    return order


@router.get("/api/orders")
async def get_orders(authorization: Optional[str] = Header(None)):
    """Get orders"""
    return list(_orders.values())


@router.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    """Get order details"""
    if order_id not in _orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return _orders[order_id]


@router.get("/api/orders/track/{order_id}")
async def track_order(order_id: int):
    """Track order"""
    if order_id not in _orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = _orders[order_id]
    status_flow = ["confirmed", "preparing", "out_for_delivery", "delivered"]
    current_index = status_flow.index(order["status"]) if order["status"] in status_flow else 0
    
    timeline = [
        {"status": "Order Confirmed", "time": order["created_at"], "completed": True},
        {"status": "Preparing", "time": None, "completed": current_index >= 1},
        {"status": "Out for Delivery", "time": None, "completed": current_index >= 2},
        {"status": "Delivered", "time": order.get("estimated_delivery") if current_index >= 3 else None, "completed": current_index >= 3}
    ]
    
    return {
        "order_id": order["id"],
        "status": order["status"],
        "estimated_delivery": order.get("estimated_delivery"),
        "timeline": timeline
    }


@router.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "products": len(_products),
        "orders": len(_orders),
        "subscriptions": len(_subscriptions)
    }
