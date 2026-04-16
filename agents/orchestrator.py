"""
FreshCart AI - Multi-Agent Orchestrator
=======================================
Orchestrates all agents defined in agents/agents.md
Parses markdown to load agent definitions and manages agent execution.
"""

import re
import pandas as pd
import random
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


# ==================== CONFIGURATION ====================

AGENTS_MD_PATH = Path(__file__).parent / "agents.md"
PRODUCTS_CSV_PATH = Path(__file__).parent.parent / "data" / "products.csv"


# ==================== AGENT DEFINITIONS (from markdown) ====================

@dataclass
class AgentDefinition:
    """Defines an agent's metadata from markdown"""
    name: str
    version: str
    description: str
    storage: str
    methods: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ==================== BASE AGENT ====================

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, definition: AgentDefinition):
        self.name = name
        self.definition = definition
        self._initialized = False
    
    def initialize(self):
        """Initialize agent resources"""
        self._initialized = True
    
    def execute(self, method: str, **kwargs) -> Any:
        """Execute a method on this agent"""
        if hasattr(self, method):
            return getattr(self, method)(**kwargs)
        raise AttributeError(f"Method '{method}' not found in {self.name}")
    
    def get_methods(self) -> List[str]:
        """Get list of available methods"""
        return [m for m in dir(self) if not m.startswith('_') and callable(getattr(self, m))]


# ==================== PRODUCT AGENT ====================

class ProductAgent(BaseAgent):
    """Agent for product catalog management"""
    
    def __init__(self, definition: AgentDefinition = None):
        super().__init__("ProductAgent", definition or self._default_definition())
        self._products = None
    
    @staticmethod
    def _default_definition() -> AgentDefinition:
        return AgentDefinition(
            name="ProductAgent",
            version="1.0.0",
            description="Manages product catalog",
            storage="csv",
            metadata={"data_source": str(PRODUCTS_CSV_PATH)}
        )
    
    def _load_products(self) -> pd.DataFrame:
        if self._products is None:
            self._products = pd.read_csv(PRODUCTS_CSV_PATH)
        return self._products
    
    def get_all_products(self) -> List[dict]:
        """Get all products from catalog"""
        df = self._load_products()
        return df.to_dict('records')
    
    def get_products_by_category(self, category: str) -> List[dict]:
        """Filter products by category"""
        df = self._load_products()
        filtered = df[df['category'].str.lower() == category.lower()]
        return filtered.to_dict('records')
    
    def search_products(self, keyword: str) -> List[dict]:
        """Search by name, category, or description"""
        df = self._load_products()
        keyword_lower = keyword.lower()
        filtered = df[
            df['name'].str.lower().str.contains(keyword_lower, na=False) |
            df['category'].str.lower().str.contains(keyword_lower, na=False) |
            df['description'].str.lower().str.contains(keyword_lower, na=False)
        ]
        return filtered.to_dict('records')
    
    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        """Get single product by ID"""
        df = self._load_products()
        product = df[df['id'] == product_id]
        if product.empty:
            return None
        return product.iloc[0].to_dict()
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        df = self._load_products()
        return df['category'].unique().tolist()
    
    def get_low_stock_products(self, threshold: int = 10) -> List[dict]:
        """Get products with low stock"""
        df = self._load_products()
        low_stock = df[df['stock'] < threshold]
        return low_stock.to_dict('records')


# ==================== CART AGENT ====================

class CartItem:
    def __init__(self, product_id: int, name: str, price: float, quantity: int, unit: str = ""):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.unit = unit
    
    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "unit": self.unit,
            "subtotal": self.price * self.quantity
        }


class CartAgent(BaseAgent):
    """Agent for shopping cart operations"""
    
    DELIVERY_FEE = 2.99
    
    def __init__(self, definition: AgentDefinition = None):
        super().__init__("CartAgent", definition or self._default_definition())
        self._cart: Dict[int, CartItem] = {}
    
    @staticmethod
    def _default_definition() -> AgentDefinition:
        return AgentDefinition(
            name="CartAgent",
            version="1.0.0",
            description="Handles shopping cart operations",
            storage="memory"
        )
    
    def add_item(self, product_id: int, name: str, price: float, quantity: int = 1, unit: str = "") -> Dict:
        """Add item to cart"""
        if product_id in self._cart:
            self._cart[product_id].quantity += quantity
        else:
            self._cart[product_id] = CartItem(product_id, name, price, quantity, unit)
        return self._cart[product_id].to_dict()
    
    def remove_item(self, product_id: int) -> bool:
        """Remove item from cart"""
        if product_id in self._cart:
            del self._cart[product_id]
            return True
        return False
    
    def update_quantity(self, product_id: int, quantity: int) -> Optional[Dict]:
        """Update item quantity"""
        if product_id not in self._cart:
            return None
        if quantity <= 0:
            return self.remove_item(product_id)
        self._cart[product_id].quantity = quantity
        return self._cart[product_id].to_dict()
    
    def view_cart(self) -> List[Dict]:
        """Get all cart items"""
        return [item.to_dict() for item in self._cart.values()]
    
    def calculate_total(self) -> Dict:
        """Calculate totals"""
        items = self.view_cart()
        subtotal = sum(item['subtotal'] for item in items)
        delivery_fee = self.DELIVERY_FEE if items else 0
        return {
            "items": items,
            "subtotal": round(subtotal, 2),
            "delivery_fee": delivery_fee,
            "total": round(subtotal + delivery_fee, 2)
        }
    
    def clear_cart(self):
        """Empty the cart"""
        self._cart.clear()
    
    def get_cart_count(self) -> int:
        return sum(item.quantity for item in self._cart.values())


# ==================== ORDER AGENT ====================

class Order:
    def __init__(self, order_id: int, items: List[Dict], total: float, address: str = "", user_id: int = None):
        self.id = order_id
        self.user_id = user_id
        self.items = items
        self.total = total
        self.address = address
        self.status = "confirmed"
        self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": self.items,
            "total": self.total,
            "address": self.address,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class OrderAgent(BaseAgent):
    """Agent for order processing"""
    
    def __init__(self, definition: AgentDefinition = None):
        super().__init__("OrderAgent", definition or self._default_definition())
        self._orders: Dict[int, Order] = {}
        self._next_id = 1
    
    @staticmethod
    def _default_definition() -> AgentDefinition:
        return AgentDefinition(
            name="OrderAgent",
            version="1.0.0",
            description="Processes customer orders",
            storage="memory",
            metadata={"statuses": ["pending", "confirmed", "preparing", "shipped", "delivered", "cancelled"]}
        )
    
    def place_order(self, items: List[Dict], total: float, address: str = "", user_id: int = None) -> Dict:
        """Create new order"""
        order = Order(self._next_id, items, total, address, user_id)
        self._orders[self._next_id] = order
        self._next_id += 1
        return order.to_dict()
    
    def get_order_history(self) -> List[Dict]:
        """Get all orders"""
        return [o.to_dict() for o in self._orders.values()]
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        """Get orders for user"""
        return [o.to_dict() for o in self._orders.values() if o.user_id == user_id]
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        """Get specific order"""
        if order_id in self._orders:
            return self._orders[order_id].to_dict()
        return None
    
    def update_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        if order_id in self._orders:
            self._orders[order_id].status = status
            return True
        return False
    
    def cancel_order(self, order_id: int) -> bool:
        """Cancel order"""
        if order_id in self._orders:
            self._orders[order_id].status = "cancelled"
            return True
        return False


# ==================== SUBSCRIPTION AGENT ====================

class SubscriptionAgent(BaseAgent):
    """Agent for subscription management"""
    
    def __init__(self, definition: AgentDefinition = None):
        super().__init__("SubscriptionAgent", definition or self._default_definition())
        self._subscriptions: Dict[int, dict] = {}
        self._next_id = 1
    
    @staticmethod
    def _default_definition() -> AgentDefinition:
        return AgentDefinition(
            name="SubscriptionAgent",
            version="1.0.0",
            description="Manages recurring subscriptions",
            storage="memory",
            metadata={"frequencies": ["daily", "weekly", "monthly"]}
        )
    
    def create_subscription(self, product_id: int, product_name: str,
                           frequency: str, quantity: int, price: float) -> Dict:
        """Create subscription"""
        valid_freqs = ["daily", "weekly", "monthly"]
        if frequency.lower() not in valid_freqs:
            raise ValueError(f"Invalid frequency. Must be one of: {valid_freqs}")
        
        days = {"daily": 1, "weekly": 7, "monthly": 30}[frequency.lower()]
        subscription = {
            "id": self._next_id,
            "product_id": product_id,
            "product_name": product_name,
            "frequency": frequency.lower(),
            "quantity": quantity,
            "price": price,
            "total": price * quantity,
            "next_delivery": (datetime.now() + timedelta(days=days)).isoformat(),
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        self._subscriptions[self._next_id] = subscription
        self._next_id += 1
        return subscription
    
    def get_active_subscriptions(self) -> List[Dict]:
        """Get active subscriptions"""
        return [s for s in self._subscriptions.values() if s["active"]]
    
    def get_user_subscriptions(self, user_id: int) -> List[Dict]:
        """Get user subscriptions"""
        return [s for s in self._subscriptions.values() if s.get("user_id") == user_id and s["active"]]
    
    def get_all_subscriptions(self) -> List[Dict]:
        """Get all subscriptions"""
        return list(self._subscriptions.values())
    
    def cancel_subscription(self, subscription_id: int) -> bool:
        """Cancel subscription"""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id]["active"] = False
            return True
        return False
    
    def reactivate_subscription(self, subscription_id: int) -> bool:
        """Reactivate subscription"""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id]["active"] = True
            return True
        return False


# ==================== NOTIFICATION AGENT ====================

class NotificationAgent(BaseAgent):
    """Agent for user notifications"""
    
    def __init__(self, definition: AgentDefinition = None):
        super().__init__("NotificationAgent", definition or self._default_definition())
        self._notifications: Dict[int, dict] = {}
        self._next_id = 1
    
    @staticmethod
    def _default_definition() -> AgentDefinition:
        return AgentDefinition(
            name="NotificationAgent",
            version="1.0.0",
            description="Manages user notifications",
            storage="memory",
            metadata={"types": ["order", "delivery", "subscription", "product", "promo"]}
        )
    
    def create_notification(self, user_id: int, notification_type: str,
                            title: str, message: str, data: dict = None) -> Dict:
        """Create notification"""
        notification = {
            "id": self._next_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False,
            "created_at": datetime.now().isoformat()
        }
        self._notifications[self._next_id] = notification
        self._next_id += 1
        return notification
    
    def create_order_notification(self, user_id: int, order_id: int, items: List[Dict]) -> Dict:
        """Create order confirmation"""
        item_names = [item.get('name', 'Item') for item in items[:3]]
        items_text = ", ".join(item_names)
        if len(items) > 3:
            items_text += f" and {len(items) - 3} more"
        
        return self.create_notification(
            user_id=user_id,
            notification_type="order",
            title="Order Confirmed!",
            message=f"Your order #{order_id} ({items_text}) has been placed.",
            data={"order_id": order_id}
        )
    
    def create_delivery_notification(self, user_id: int, order_id: int,
                                   status: str, message: str) -> Dict:
        """Create delivery update"""
        return self.create_notification(
            user_id=user_id,
            notification_type="delivery",
            title=f"Delivery Update - Order #{order_id}",
            message=message,
            data={"order_id": order_id, "status": status}
        )
    
    def create_subscription_notification(self, user_id: int, subscription_id: int,
                                       product_name: str, action: str) -> Dict:
        """Create subscription notification"""
        return self.create_notification(
            user_id=user_id,
            notification_type="subscription",
            title=f"Subscription {action.title()}!",
            message=f"Your subscription for {product_name} has been {action}.",
            data={"subscription_id": subscription_id}
        )
    
    def create_product_notification(self, user_id: int, product_id: int,
                                   product_name: str) -> Dict:
        """Create product alert"""
        return self.create_notification(
            user_id=user_id,
            notification_type="product",
            title="New Product Alert!",
            message=f"Check out our new {product_name} - now available!",
            data={"product_id": product_id}
        )
    
    def get_user_notifications(self, user_id: int) -> List[Dict]:
        """Get user notifications"""
        return [n for n in self._notifications.values() if n["user_id"] == user_id]
    
    def get_unread_count(self, user_id: int) -> int:
        """Get unread count"""
        return sum(1 for n in self._notifications.values() if n["user_id"] == user_id and not n["read"])
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark as read"""
        if notification_id in self._notifications:
            self._notifications[notification_id]["read"] = True
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all as read"""
        count = 0
        for n in self._notifications.values():
            if n["user_id"] == user_id and not n["read"]:
                n["read"] = True
                count += 1
        return count
    
    def delete_notification(self, notification_id: int) -> bool:
        """Delete notification"""
        if notification_id in self._notifications:
            del self._notifications[notification_id]
            return True
        return False


# ==================== RECOMMENDATION AGENT ====================

class RecommendationAgent(BaseAgent):
    """Agent for product recommendations"""
    
    def __init__(self, product_agent: ProductAgent, definition: AgentDefinition = None):
        super().__init__("RecommendationAgent", definition or self._default_definition())
        self.product_agent = product_agent
    
    @staticmethod
    def _default_definition() -> AgentDefinition:
        return AgentDefinition(
            name="RecommendationAgent",
            version="1.0.0",
            description="Provides product recommendations",
            storage="none"
        )
    
    def recommend_by_product(self, product_id: int) -> List[Dict]:
        """Get similar products"""
        product = self.product_agent.get_product_by_id(product_id)
        if not product:
            return []
        return self.recommend_by_category(product['category'])
    
    def recommend_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """Get products from category"""
        products = self.product_agent.get_products_by_category(category)
        if len(products) <= limit:
            return products
        return random.sample(products, limit)
    
    def get_popular_products(self, limit: int = 10) -> List[Dict]:
        """Get popular products"""
        all_products = self.product_agent.get_all_products()
        if len(all_products) <= limit:
            return all_products
        return random.sample(all_products, limit)
    
    def get_complementary_products(self, product_id: int) -> List[Dict]:
        """Get complementary products"""
        product = self.product_agent.get_product_by_id(product_id)
        if not product:
            return []
        
        complementary = {'vegetables': 'fruits', 'fruits': 'nuts', 'nuts': 'vegetables'}
        related = complementary.get(product['category'], 'vegetables')
        return self.recommend_by_category(related, limit=3)
    
    def get_bundle_suggestions(self, cart_items: List[Dict]) -> List[Dict]:
        """Suggest bundle items"""
        categories = set(item.get('category', '') for item in cart_items)
        suggestions = []
        for category in ['vegetables', 'fruits', 'nuts']:
            if category not in categories:
                products = self.product_agent.get_products_by_category(category)
                if products:
                    suggestions.append(random.choice(products))
        return suggestions


# ==================== ORCHESTRATOR ====================

class AgentOrchestrator:
    """
    Multi-Agent Orchestrator
    Manages all agents and orchestrates workflows
    """
    
    def __init__(self, agents_md_path: str = None):
        self.agents_md_path = Path(agents_md_path) if agents_md_path else AGENTS_MD_PATH
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, List[str]] = {}
        self._initialize_agents()
        self._parse_markdown()
    
    def _initialize_agents(self):
        """Initialize all agents"""
        product = ProductAgent()
        product.initialize()
        self.agents["ProductAgent"] = product
        
        self.agents["CartAgent"] = CartAgent()
        self.agents["OrderAgent"] = OrderAgent()
        self.agents["SubscriptionAgent"] = SubscriptionAgent()
        self.agents["NotificationAgent"] = NotificationAgent()
        
        self.agents["RecommendationAgent"] = RecommendationAgent(product)
    
    def _parse_markdown(self):
        """Parse markdown to extract agent definitions and workflows"""
        if not self.agents_md_path.exists():
            return
        
        content = self.agents_md_path.read_text(encoding='utf-8')
        
        agent_pattern = r'## (\w+)\s+```yaml\s+(.*?)```'
        matches = re.findall(agent_pattern, content, re.DOTALL)
        
        for name, yaml_content in matches:
            if name in self.agents:
                self.agents[name].definition = self._parse_yaml(yaml_content)
        
        workflow_pattern = r'### Workflow: (\w+)\s+(.*?)(?=###|\Z)'
        workflow_matches = re.findall(workflow_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for name, content in workflow_matches:
            agent_list = re.findall(r'\d+\.\s+\*\*(\w+)\*\*', content)
            self.workflows[name] = agent_list
    
    def _parse_yaml(self, yaml_str: str) -> AgentDefinition:
        """Parse simple YAML frontmatter"""
        lines = yaml_str.strip().split('\n')
        definition = AgentDefinition(
            name="",
            version="1.0.0",
            description="",
            storage="memory"
        )
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'name':
                    definition.name = value
                elif key == 'version':
                    definition.version = value
                elif key == 'description':
                    definition.description = value
                elif key == 'storage':
                    definition.storage = value
                elif value.startswith('[') and value.endswith(']'):
                    definition.metadata[key] = [v.strip() for v in value[1:-1].split(',')]
                else:
                    definition.metadata[key] = value
        
        return definition
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def execute_workflow(self, workflow_name: str, context: Dict = None) -> Dict:
        """Execute a predefined workflow"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        context = context or {}
        results = []
        
        for agent_name in self.workflows[workflow_name]:
            agent = self.get_agent(agent_name)
            if not agent:
                continue
            
            results.append({
                "agent": agent_name,
                "status": "executed",
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "workflow": workflow_name,
            "results": results,
            "context": context
        }
    
    def list_agents(self) -> List[str]:
        """List all available agents"""
        return list(self.agents.keys())
    
    def list_workflows(self) -> List[str]:
        """List all available workflows"""
        return list(self.workflows.keys())


# ==================== GLOBAL INSTANCE ====================

orchestrator = AgentOrchestrator()


# ==================== CONVENIENCE ACCESSORS ====================

def get_product_agent() -> ProductAgent:
    return orchestrator.get_agent("ProductAgent")

def get_cart_agent() -> CartAgent:
    return orchestrator.get_agent("CartAgent")

def get_order_agent() -> OrderAgent:
    return orchestrator.get_agent("OrderAgent")

def get_subscription_agent() -> SubscriptionAgent:
    return orchestrator.get_agent("SubscriptionAgent")

def get_notification_agent() -> NotificationAgent:
    return orchestrator.get_agent("NotificationAgent")

def get_recommendation_agent() -> RecommendationAgent:
    return orchestrator.get_agent("RecommendationAgent")
