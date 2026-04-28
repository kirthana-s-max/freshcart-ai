from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime

from api.models.schemas import (
    UserCreate, User, LoginRequest, AuthResponse,
    Product, Subscription, SubscriptionCreate,
    Order, OrderCreate, CartResponse, CartItem
)
from api.routes.user_routes import user_store
from api.routes.product_routes import router 

app = FastAPI(title="FreshCart AI", version="1.0.0", description="Subscription-based grocery delivery platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to FreshCart AI", "version": "1.0.0"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============= AUTH ROUTES =============
@app.post("/api/auth/register", response_model=AuthResponse)
async def register(user: UserCreate, password: str = "freshcart123"):
    try:
        result = user_store.create_user(
            name=user.name,
            email=user.email,
            phone=user.phone,
            address=user.address,
            password=password  
        ) 
        return result 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    result = user_store.authenticate(request.email, request.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result

@app.get("/api/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = user_store.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# ============= PRODUCT ROUTES =============
@app.get("/api/products", response_model=List[Product])
async def get_products():
    return product_store.get_all()

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = product_store.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/products/category/{category}", response_model=List[Product])
async def get_products_by_category(category: str):
    return product_store.get_by_category(category)

@app.get("/api/search")
async def search_products(q: str):
    return product_store.search(q)

@app.get("/api/categories")
async def get_categories():
    return product_store.get_categories()

# ============= SUBSCRIPTION ROUTES =============
@app.post("/api/subscriptions", response_model=Subscription)
async def create_subscription(
    sub: SubscriptionCreate,
    authorization: Optional[str] = Header(None)
):
    product = product_store.get_by_id(sub.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    user_id = None
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = user_store.get_user_by_token(token)
        if user:
            user_id = user["id"]
    
    subscription = subscription_store.create(
        user_id=user_id,
        product_id=sub.product_id,
        product_name=product["name"],
        frequency=sub.frequency.value,
        quantity=sub.quantity,
        price=product["price"]
    )
    return subscription

@app.get("/api/subscriptions", response_model=List[Subscription])
async def get_subscriptions(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = user_store.get_user_by_token(token)
        if user:
            return subscription_store.get_user_subscriptions(user["id"])
    return subscription_store.get_all()

@app.delete("/api/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: int):
    success = subscription_store.cancel(subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription cancelled"}

# ============= CART ROUTES =============
@app.post("/api/cart/add")
async def add_to_cart(
    product_id: int,
    quantity: int = 1,
    authorization: Optional[str] = Header(None)
):
    product = product_store.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "message": "Added to cart",
        "product": product,
        "quantity": quantity
    }

@app.get("/api/cart", response_model=CartResponse)
async def get_cart(authorization: Optional[str] = Header(None)):
    items = []
    subtotal = 0.0
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = user_store.get_user_by_token(token)
        if user:
            for item in user.get("cart", []):
                product = product_store.get_by_id(item["product_id"])
                if product:
                    item_total = product["price"] * item["quantity"]
                    items.append(CartItem(
                        product_id=product["id"],
                        name=product["name"],
                        price=product["price"],
                        quantity=item["quantity"],
                        unit=product["unit"],
                        subtotal=item_total
                    ))
                    subtotal += item_total
    
    delivery_fee = 2.99
    return CartResponse(
        items=items,
        subtotal=round(subtotal, 2),
        delivery_fee=delivery_fee,
        total=round(subtotal + delivery_fee, 2)
    )

# ============= ORDER ROUTES =============
@app.post("/api/orders", response_model=Order)
async def place_order(
    order: OrderCreate,
    authorization: Optional[str] = Header(None)
):
    if not order.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    user_id = None
    address = order.address
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = user_store.get_user_by_token(token)
        if user:
            user_id = user["id"]
            address = user.get("address", order.address)
    
    subtotal = sum(item.subtotal for item in order.items)
    delivery_fee = 2.99
    total = subtotal + delivery_fee
    
    items = [item.model_dump() for item in order.items]
    
    new_order = order_store.create(
        user_id=user_id,
        items=items,
        subtotal=round(subtotal, 2),
        delivery_fee=delivery_fee,
        total=round(total, 2),
        address=address,
        payment_method=order.payment_method
    )
    
    return new_order

@app.get("/api/orders", response_model=List[Order])
async def get_orders(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = user_store.get_user_by_token(token)
        if user:
            return order_store.get_user_orders(user["id"])
    return order_store.get_all()

@app.get("/api/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    order = order_store.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/orders/track/{order_id}")
async def track_order(order_id: int):
    order = order_store.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    statuses = ["confirmed", "preparing", "out_for_delivery", "delivered"]
    current_index = statuses.index(order["status"]) if order["status"] in statuses else 0
    
    return {
        "order_id": order["id"],
        "status": order["status"],
        "progress": (current_index + 1) / len(statuses) * 100,
        "estimated_delivery": order.get("estimated_delivery"),
        "timeline": [
            {"status": "Order Confirmed", "time": order["created_at"], "completed": True},
            {"status": "Preparing", "time": None, "completed": current_index >= 1},
            {"status": "Out for Delivery", "time": None, "completed": current_index >= 2},
            {"status": "Delivered", "time": None, "completed": current_index >= 3}
        ]
    }

# ============= SUBSCRIPTION PLANS =============
@app.get("/api/subscription-plans")
async def get_subscription_plans():
    return [
        {
            "id": "daily",
            "name": "Daily Fresh",
            "description": "Get fresh delivery every day",
            "icon": "📅",
            "benefits": ["Daily delivery", "Always fresh", "Flexible skip"]
        },
        {
            "id": "weekly",
            "name": "Weekly Bundle",
            "description": "Weekly delivery with savings",
            "icon": "📦",
            "benefits": ["Weekly delivery", "10% off", "Free delivery"]
        },
        {
            "id": "monthly",
            "name": "Monthly Mega",
            "description": "Monthly subscription with best savings",
            "icon": "🎁",
            "benefits": ["Monthly delivery", "20% off", "Priority support", "Free delivery"]
        }
    ]

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass

from agents.orchestrator import Orchestrator

orch = Orchestrator()

@app.get("/run/{endpoint}")
def run(endpoint: str):
    return orch.run_flow(endpoint, {})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
