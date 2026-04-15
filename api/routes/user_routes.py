"""
User Routes - Authentication and User Management
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime
import uuid
import hashlib

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory storage (shared with main.py)
_users = {}
_sessions = {}
_next_user_id = 1


def init_demo_user():
    """Initialize demo user"""
    global _next_user_id
    _users[1] = {
        "id": 1,
        "name": "Demo User",
        "email": "demo@freshcart.ai",
        "phone": "+91 9876543210",
        "address": "123 Demo Street, Mumbai, India",
        "password": _hash_password("demo123"),
        "created_at": datetime.now()
    }
    _next_user_id = 2


def _hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_current_user(token: str) -> Optional[dict]:
    """Get user by token"""
    user_id = _sessions.get(token)
    if user_id:
        user = _users.get(user_id)
        if user:
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"],
                "address": user["address"],
                "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
            }
    return None


# Initialize demo user on module load
init_demo_user()


@router.post("/register")
async def register(name: str, email: str, phone: str, address: str, password: str = "password123"):
    """Register a new user"""
    global _next_user_id
    
    if any(u["email"] == email for u in _users.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "id": _next_user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "password": _hash_password(password),
        "created_at": datetime.now()
    }
    
    _users[_next_user_id] = user
    
    token = str(uuid.uuid4())
    _sessions[token] = _next_user_id
    _next_user_id += 1
    
    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "address": user["address"],
        "created_at": user["created_at"].isoformat()
    }
    
    return {"user": user_data, "token": token}


@router.post("/login")
async def login(email: str, password: str):
    """Login user and return token"""
    for user in _users.values():
        if user["email"] == email and user["password"] == _hash_password(password):
            token = str(uuid.uuid4())
            _sessions[token] = user["id"]
            
            user_data = {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"],
                "address": user["address"],
                "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
            }
            
            return {"user": user_data, "token": token}
    
    raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/me")
async def get_me(authorization: Optional[str] = Header(None)):
    """Get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user
