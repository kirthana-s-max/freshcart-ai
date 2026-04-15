"""
FreshCart AI - API Routes Module
"""

from .routes.user_routes import router as user_router
from .routes.product_routes import router as product_router 

__all__ = ['user_router', 'product_router']
